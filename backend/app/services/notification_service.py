from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from app.models.notification_settings import NotificationSettings
from app.schemas.notification import NotificationSettingsCreate, NotificationSettingsUpdate
import redis
import json
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.redis_client = redis.from_url(settings.REDIS_URL)

    def get_user_settings(self, user_id: int) -> Optional[NotificationSettings]:
        return self.db.query(NotificationSettings).filter(
            NotificationSettings.user_id == user_id
        ).first()

    def create_settings(
        self,
        settings_data: NotificationSettingsCreate,
        user_id: int
    ) -> NotificationSettings:
        existing = self.get_user_settings(user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Settings already exist"
            )
        
        settings = NotificationSettings(
            user_id=user_id,
            email=settings_data.email,
            telegram_chat_id=settings_data.telegram_chat_id,
            email_enabled=settings_data.email_enabled,
            telegram_enabled=settings_data.telegram_enabled,
            event_types=settings_data.event_types
        )
        self.db.add(settings)
        self.db.commit()
        self.db.refresh(settings)
        return settings

    def update_settings(
        self,
        settings_data: NotificationSettingsUpdate,
        user_id: int
    ) -> Optional[NotificationSettings]:
        settings = self.get_user_settings(user_id)
        if not settings:
            return None
        
        if settings_data.email is not None:
            settings.email = settings_data.email
        if settings_data.telegram_chat_id is not None:
            settings.telegram_chat_id = settings_data.telegram_chat_id
        if settings_data.email_enabled is not None:
            settings.email_enabled = settings_data.email_enabled
        if settings_data.telegram_enabled is not None:
            settings.telegram_enabled = settings_data.telegram_enabled
        if settings_data.event_types is not None:
            settings.event_types = settings_data.event_types
        
        self.db.commit()
        self.db.refresh(settings)
        return settings

    def send_notification(
        self,
        user_id: int,
        event_type: str,
        data: Dict[str, Any]
    ):
        user_settings = self.get_user_settings(user_id)
        if not user_settings:
            return
        
        if event_type not in user_settings.event_types:
            return
        
        notification_task = {
            "user_id": user_id,
            "event_type": event_type,
            "data": data,
            "email_enabled": user_settings.email_enabled,
            "telegram_enabled": user_settings.telegram_enabled,
            "email": user_settings.email,
            "telegram_chat_id": user_settings.telegram_chat_id
        }
        
        self.redis_client.lpush("notification_queue", json.dumps(notification_task))

    async def send_email_async(self, to_email: str, subject: str, body: str):
        if not settings.SMTP_HOST or not settings.SMTP_USER:
            return
        
        message = MIMEMultipart()
        message["From"] = settings.SMTP_USER
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))
        
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=True
        )
