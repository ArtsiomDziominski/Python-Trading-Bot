from pydantic import BaseModel
from datetime import datetime
from app.models.bot import BotStatus, Exchange
from typing import Optional

class BotCreate(BaseModel):
    name: str
    exchange: Exchange
    strategy: str
    symbol: str
    api_key: str
    api_secret: str
    config: Optional[str] = None

class BotUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[BotStatus] = None
    config: Optional[str] = None

class BotResponse(BaseModel):
    id: int
    user_id: int
    name: str
    exchange: Exchange
    strategy: str
    symbol: str
    status: BotStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
