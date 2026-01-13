from sqlalchemy.orm import Session
from app.models.user import User
from app.models.notification_settings import NotificationSettings

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_or_create_user_by_telegram(self, telegram_chat_id: str) -> int:
        settings = self.db.query(NotificationSettings).filter(
            NotificationSettings.telegram_chat_id == telegram_chat_id
        ).first()
        
        if settings:
            return settings.user_id
        
        return None
