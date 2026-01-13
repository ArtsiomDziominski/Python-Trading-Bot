import asyncio
import json
import redis
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.order import Order, OrderStatus
from app.services.exchange_service import ExchangeService
from app.services.bot_service import BotService
from app.services.notification_service import NotificationService
from app.config import settings

class OrderMonitor:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.exchange_service = ExchangeService()
        self.running = True

    async def start(self):
        while self.running:
            try:
                message = self.redis_client.brpop("order_monitoring_queue", timeout=1)
                if message:
                    _, data = message
                    task = json.loads(data)
                    await self.process_order(task.get("order_id"))
            except Exception as e:
                print(f"Error in order monitor: {e}")
            await asyncio.sleep(1)

    async def process_order(self, order_id: int):
        db = SessionLocal()
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return

            bot = order.bot
            bot_service = BotService(db)
            api_key = bot_service._decrypt(bot.api_key_encrypted)
            api_secret = bot_service._decrypt(bot.api_secret_encrypted)

            exchange_order = self.exchange_service.get_order_status(
                exchange_name=bot.exchange,
                api_key=api_key,
                api_secret=api_secret,
                order_id=order.exchange_order_id,
                symbol=order.symbol
            )

            new_status = self._map_exchange_status(exchange_order.get("status"))
            
            if new_status != order.status:
                old_status = order.status
                order.status = new_status
                order.filled_quantity = exchange_order.get("filled", 0)
                db.commit()

                notification_service = NotificationService(db)
                notification_service.send_notification(
                    user_id=bot.user_id,
                    event_type="order_filled" if new_status == OrderStatus.FILLED else "order_cancelled",
                    data={
                        "order_id": order.id,
                        "symbol": order.symbol,
                        "old_status": old_status.value,
                        "new_status": new_status.value
                    }
                )
        finally:
            db.close()

    def _map_exchange_status(self, exchange_status: str) -> OrderStatus:
        status_map = {
            "open": OrderStatus.OPEN,
            "closed": OrderStatus.FILLED,
            "canceled": OrderStatus.CANCELLED,
            "cancelled": OrderStatus.CANCELLED,
            "filled": OrderStatus.FILLED,
            "partial": OrderStatus.OPEN
        }
        return status_map.get(exchange_status.lower(), OrderStatus.PENDING)

    def stop(self):
        self.running = False
