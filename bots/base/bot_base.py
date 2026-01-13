from abc import ABC, abstractmethod
from typing import Optional

class BotBase(ABC):
    def __init__(self, bot_id: int, db_session, redis_client):
        self.bot_id = bot_id
        self.db = db_session
        self.redis = redis_client
        self.exchange_client = None
    
    def initialize(self):
        # TODO: Загрузка конфигурации из БД
        # TODO: Инициализация клиента биржи
        pass
    
    def run(self):
        # TODO: Основной цикл бота
        # TODO: Получение задач из Redis
        # TODO: Выполнение логики
        pass
    
    @abstractmethod
    def execute_strategy(self):
        # Абстрактный метод - реализуется в каждом боте
        raise NotImplementedError("Метод будет реализован позже")
