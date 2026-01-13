import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from app.bot import TradingBot
from app.utils.database import get_db
from app.utils.redis_client import get_redis
from app.config import settings

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, settings.LOG_LEVEL)
)

async def main():
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    bot = TradingBot(application)
    bot.setup_handlers()
    
    db = next(get_db())
    redis_client = get_redis()
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    await bot.start_message_worker(db, redis_client)
    
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
