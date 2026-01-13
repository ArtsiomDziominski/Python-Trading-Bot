from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.bot import Bot, BotStatus
from app.schemas.bot import BotCreate, BotUpdate
from app.services.exchange_service import ExchangeService
from cryptography.fernet import Fernet
from app.config import settings
import base64
import hashlib

class BotService:
    def __init__(self, db: Session):
        self.db = db
        self.exchange_service = ExchangeService()
        self._cipher = None

    def _get_cipher(self) -> Fernet:
        if self._cipher is None:
            key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
            key_b64 = base64.urlsafe_b64encode(key)
            self._cipher = Fernet(key_b64)
        return self._cipher

    def _encrypt(self, data: str) -> str:
        cipher = self._get_cipher()
        return cipher.encrypt(data.encode()).decode()

    def _decrypt(self, encrypted_data: str) -> str:
        cipher = self._get_cipher()
        return cipher.decrypt(encrypted_data.encode()).decode()

    def create_bot(self, bot_data: BotCreate, user_id: int) -> Bot:
        api_key_encrypted = self._encrypt(bot_data.api_key)
        api_secret_encrypted = self._encrypt(bot_data.api_secret)
        
        bot = Bot(
            user_id=user_id,
            name=bot_data.name,
            exchange=bot_data.exchange,
            strategy=bot_data.strategy,
            symbol=bot_data.symbol,
            api_key_encrypted=api_key_encrypted,
            api_secret_encrypted=api_secret_encrypted,
            config=bot_data.config,
            status=BotStatus.STOPPED
        )
        self.db.add(bot)
        self.db.commit()
        self.db.refresh(bot)
        return bot

    def get_user_bots(self, user_id: int) -> List[Bot]:
        return self.db.query(Bot).filter(Bot.user_id == user_id).all()

    def get_bot(self, bot_id: int, user_id: int) -> Optional[Bot]:
        return self.db.query(Bot).filter(
            Bot.id == bot_id,
            Bot.user_id == user_id
        ).first()

    def update_bot(self, bot_id: int, bot_data: BotUpdate, user_id: int) -> Optional[Bot]:
        bot = self.get_bot(bot_id, user_id)
        if not bot:
            return None
        
        if bot_data.name is not None:
            bot.name = bot_data.name
        if bot_data.status is not None:
            bot.status = bot_data.status
        if bot_data.config is not None:
            bot.config = bot_data.config
        
        self.db.commit()
        self.db.refresh(bot)
        return bot

    def delete_bot(self, bot_id: int, user_id: int) -> bool:
        bot = self.get_bot(bot_id, user_id)
        if not bot:
            return False
        self.db.delete(bot)
        self.db.commit()
        return True
