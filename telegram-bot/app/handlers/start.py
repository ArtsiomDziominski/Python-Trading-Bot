from telegram import Update
from telegram.ext import ContextTypes
from app.utils.database import get_db
from app.services.user_service import UserService

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = next(get_db())
    user_service = UserService(db)
    
    chat_id = str(update.effective_chat.id)
    user_id = await user_service.get_or_create_user_by_telegram(chat_id)
    
    await update.message.reply_text(
        f"Привет! Твой chat_id: {chat_id}\n"
        "Используй /settings для настройки уведомлений"
    )
