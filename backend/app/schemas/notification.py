from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class NotificationSettingsCreate(BaseModel):
    email: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    email_enabled: bool = True
    telegram_enabled: bool = True
    event_types: List[str] = []

class NotificationSettingsUpdate(BaseModel):
    email: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    email_enabled: Optional[bool] = None
    telegram_enabled: Optional[bool] = None
    event_types: Optional[List[str]] = None

class NotificationSettingsResponse(BaseModel):
    id: int
    user_id: int
    email: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    email_enabled: bool
    telegram_enabled: bool
    event_types: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
