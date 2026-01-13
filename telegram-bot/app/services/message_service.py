from telegram import Bot
from typing import Dict, Any

class MessageService:
    def __init__(self, db, redis_client, bot: Bot):
        self.db = db
        self.redis_client = redis_client
        self.bot = bot
    
    async def send_notification(self, notification: Dict[str, Any]):
        if not notification.get("telegram_enabled"):
            return
        
        chat_id = notification.get("telegram_chat_id")
        if not chat_id:
            return
        
        event_type = notification.get("event_type")
        data = notification.get("data", {})
        
        message = self._format_message(event_type, data)
        
        try:
            await self.bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
    
    def _format_message(self, event_type: str, data: Dict[str, Any]) -> str:
        messages = {
            "bot_created": f"✅ Бот создан: {data.get('bot_name', 'N/A')}",
            "bot_stopped": f"⏹ Бот остановлен: {data.get('bot_name', 'N/A')}",
            "order_placed": f"📊 Ордер выставлен: {data.get('symbol', 'N/A')} {data.get('side', 'N/A')}",
            "order_filled": f"✅ Ордер исполнен: {data.get('symbol', 'N/A')}",
            "order_cancelled": f"❌ Ордер отменен: {data.get('symbol', 'N/A')}",
            "exchange_error": f"⚠️ Ошибка биржи: {data.get('message', 'N/A')}",
            "bot_error": f"🔴 Ошибка бота: {data.get('message', 'N/A')}",
            "target_reached": f"🎯 Цель достигнута: {data.get('message', 'N/A')}"
        }
        return messages.get(event_type, f"Уведомление: {event_type}")
