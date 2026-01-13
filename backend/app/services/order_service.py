from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
from app.models.order import Order, OrderStatus
from app.models.bot import Bot
from app.schemas.order import OrderCreate
from app.services.exchange_service import ExchangeService
from app.services.bot_service import BotService
from app.services.notification_service import NotificationService
import redis
from app.config import settings
import json

class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.exchange_service = ExchangeService()
        self.bot_service = BotService(db)
        self.notification_service = NotificationService(db)
        self.redis_client = redis.from_url(settings.REDIS_URL)

    def create_order(self, order_data: OrderCreate, user_id: int) -> Order:
        bot = self.bot_service.get_bot(order_data.bot_id, user_id)
        if not bot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bot not found"
            )
        
        api_key = self.bot_service._decrypt(bot.api_key_encrypted)
        api_secret = self.bot_service._decrypt(bot.api_secret_encrypted)
        
        exchange_order = self.exchange_service.create_order(
            exchange_name=bot.exchange,
            api_key=api_key,
            api_secret=api_secret,
            symbol=order_data.symbol,
            side=order_data.side.value,
            type=order_data.type.value,
            amount=float(order_data.quantity),
            price=float(order_data.price) if order_data.price else None
        )
        
        order = Order(
            bot_id=order_data.bot_id,
            exchange_order_id=exchange_order.get('id'),
            symbol=order_data.symbol,
            side=order_data.side,
            type=order_data.type,
            status=OrderStatus.OPEN,
            price=order_data.price,
            quantity=order_data.quantity
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        
        self._add_to_monitoring_queue(order.id)
        self.notification_service.send_notification(
            user_id=user_id,
            event_type="order_placed",
            data={"order_id": order.id, "symbol": order.symbol, "side": order.side.value}
        )
        
        return order

    def get_user_orders(self, user_id: int, bot_id: Optional[int] = None) -> List[Order]:
        query = self.db.query(Order).join(Bot).filter(Bot.user_id == user_id)
        if bot_id:
            query = query.filter(Order.bot_id == bot_id)
        return query.all()

    def get_order(self, order_id: int, user_id: int) -> Optional[Order]:
        return self.db.query(Order).join(Bot).filter(
            Order.id == order_id,
            Bot.user_id == user_id
        ).first()

    def _add_to_monitoring_queue(self, order_id: int):
        task = {
            "order_id": order_id,
            "action": "monitor"
        }
        self.redis_client.lpush("order_monitoring_queue", json.dumps(task))
