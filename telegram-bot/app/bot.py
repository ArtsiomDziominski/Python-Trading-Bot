from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update
from app.handlers.start import start_handler
from app.handlers.notifications import notifications_handler
from app.handlers.settings import settings_handler
from app.services.message_service import MessageService
import asyncio
import json
import redis

class TradingBot:
    def __init__(self, application: Application):
        self.application = application
    
    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", start_handler))
        self.application.add_handler(CommandHandler("notifications", notifications_handler))
        self.application.add_handler(CommandHandler("settings", settings_handler))
    
    async def start_message_worker(self, db, redis_client: redis.Redis):
        message_service = MessageService(db, redis_client, self.application.bot)
        while True:
            try:
                message = redis_client.brpop("notification_queue", timeout=1)
                if message:
                    _, data = message
                    notification = json.loads(data)
                    await message_service.send_notification(notification)
            except Exception as e:
                print(f"Error processing notification: {e}")
            await asyncio.sleep(0.1)
