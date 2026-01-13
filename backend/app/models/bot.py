from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class BotStatus(str, enum.Enum):
    ACTIVE = "active"
    STOPPED = "stopped"
    ERROR = "error"

class Exchange(str, enum.Enum):
    BINANCE = "binance"
    BYBIT = "bybit"

class Bot(Base):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    exchange = Column(Enum(Exchange), nullable=False)
    strategy = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    status = Column(Enum(BotStatus), default=BotStatus.STOPPED)
    api_key_encrypted = Column(Text, nullable=False)
    api_secret_encrypted = Column(Text, nullable=False)
    config = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="bots")
    orders = relationship("Order", back_populates="bot")
