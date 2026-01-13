---
name: Trading Bot Backend
overview: Разработка бэкенда на FastAPI для создания и управления торговыми ботами для Binance, Bybit, OKX и Bitget с системой регистрации, отслеживанием ордеров и автоматическими действиями
todos:
  - id: setup-infrastructure
    content: Настроить Docker Compose с PostgreSQL, Redis и FastAPI. Создать базовую структуру проекта, requirements.txt, Dockerfile, .env.example
    status: completed
  - id: database-setup
    content: Настроить SQLAlchemy, создать модели User, Bot, Order, BotConfig. Настроить Alembic для миграций
    status: completed
    dependencies:
      - setup-infrastructure
  - id: auth-system
    content: "Реализовать систему аутентификации: регистрация, JWT токены, хеширование паролей, защищенные роуты"
    status: completed
    dependencies:
      - database-setup
  - id: exchange-integration
    content: Создать сервис для работы с Binance, Bybit, OKX и Bitget через ccxt. Реализовать шифрование API ключей
    status: completed
    dependencies:
      - database-setup
  - id: bot-management
    content: Реализовать CRUD API для управления ботами. Валидация параметров, сохранение конфигурации
    status: completed
    dependencies:
      - auth-system
      - exchange-integration
  - id: order-system
    content: "Реализовать систему ордеров: выставление, сохранение в БД, добавление в очередь мониторинга"
    status: completed
    dependencies:
      - bot-management
  - id: bot-architecture
    content: Создать архитектурные заглушки для ботов (структура папок, базовые файлы, Dockerfile). Полная реализация будет позже
    status: completed
    dependencies:
      - order-system
  - id: order-monitoring
    content: Реализовать отслеживание статусов ордеров внутри ботов через Redis Queue. Автоматические действия при изменении статуса
    status: completed
    dependencies:
      - bot-architecture
  - id: logging-monitoring
    content: Добавить логирование операций, endpoints для истории и статистики, health checks
    status: completed
    dependencies:
      - order-monitoring
  - id: notification-system
    content: "Реализовать систему уведомлений: Telegram бот в отдельном контейнере, Email сервис, настройки уведомлений пользователей"
    status: completed
    dependencies:
      - logging-monitoring
---

# План разработки бэкенда для торговых ботов Binance, Bybit, OKX и Bitget

## Архитектура системы

### Общая схема

Система построена на микросервисной архитектуре с использованием Docker контейнеров:

```mermaid
graph TB
    Client[Клиент] --> API[FastAPI Backend API]
    API --> Auth[Auth Service]
    API --> BotService[Bot Management Service]
    API --> OrderService[Order Service]
    API --> NotificationService[Notification Service]
    
    BotService --> DB[(PostgreSQL)]
    OrderService --> DB
    Auth --> DB
    NotificationService --> DB
    
    BotService --> Redis[Redis Queue]
    OrderService --> Redis
    NotificationService --> Redis
    
    Redis --> Bot1[Bot Container 1<br/>Grid Bot]
    Redis --> Bot2[Bot Container 2<br/>DCA Bot]
    Redis --> Bot3[Bot Container 3<br/>Custom Strategy]
    
    Bot1 --> BinanceAPI[Binance API]
    Bot1 --> BybitAPI[Bybit API]
    Bot1 --> OKXAPI[OKX API]
    Bot1 --> BitgetAPI[Bitget API]
    Bot2 --> BinanceAPI
    Bot2 --> BybitAPI
    Bot2 --> OKXAPI
    Bot2 --> BitgetAPI
    Bot3 --> BinanceAPI
    Bot3 --> BybitAPI
    Bot3 --> OKXAPI
    Bot3 --> BitgetAPI
    
    Bot1 --> DB
    Bot2 --> DB
    Bot3 --> DB
    
    Redis --> TelegramBot[Telegram Bot Container]
    TelegramBot --> TelegramAPI[Telegram Bot API]
    TelegramBot --> DB
    NotificationService --> EmailService[Email Service]
    EmailService --> SMTP[SMTP Server]
```

### Компоненты системы

#### 1. FastAPI Backend (Основной API сервер)

**Назначение:**
- Предоставляет REST API для управления системой
- Обрабатывает запросы от клиентов
- Управляет пользователями, ботами и ордерами
- Координирует работу всех компонентов

**Основные модули:**

**Аутентификация (`app/api/auth.py`)**
- Регистрация новых пользователей
- Вход в систему (JWT токены)
- Получение информации о текущем пользователе

**Принцип работы:**
1. Пользователь регистрируется с email и паролем
2. Пароль хешируется через bcrypt
3. При входе генерируется JWT токен
4. Токен используется для доступа к защищенным endpoints

**Управление ботами (`app/api/bots.py`)**
- Создание ботов с параметрами стратегии
- Просмотр списка ботов пользователя
- Обновление настроек бота
- Удаление ботов

**Принцип работы:**
1. Пользователь создает бота через API
2. API ключи биржи шифруются (AES/Fernet)
3. Конфигурация бота сохраняется в БД
4. Бот получает команды через Redis Queue

**Система ордеров (`app/api/orders.py`)**
- Выставление ордеров на биржу
- Просмотр истории ордеров
- Отслеживание статусов

**Принцип работы:**
1. Пользователь создает ордер через API
2. Система расшифровывает API ключи бота
3. Ордер отправляется на биржу через ccxt
4. Ордер сохраняется в БД
5. Задача мониторинга добавляется в Redis Queue

**Уведомления (`app/api/notifications.py`)**
- Настройка каналов уведомлений (Email, Telegram)
- Выбор типов событий для уведомлений
- Управление настройками

#### 2. PostgreSQL (База данных)

**Хранимые данные:**

**Таблица `users`**
- Информация о пользователях
- Email, хешированный пароль
- Статус активности

**Таблица `bots`**
- Конфигурация ботов
- Зашифрованные API ключи бирж
- Статус бота (активен/остановлен)
- Параметры стратегии

**Таблица `orders`**
- История всех ордеров
- Статусы ордеров
- Связь с ботами и биржами

**Таблица `notification_settings`**
- Настройки уведомлений пользователей
- Email адреса
- Telegram chat_id
- Включенные типы событий

#### 3. Redis (Очереди и кеш)

**Использование:**

**Очередь мониторинга ордеров (`order_monitoring_queue`)**
- Задачи на проверку статусов ордеров
- Формат: `{"order_id": 123, "action": "monitor"}`

**Очередь уведомлений (`notification_queue`)**
- Задачи на отправку уведомлений
- Формат: `{"user_id": 1, "event_type": "order_filled", "data": {...}}`

**Принцип работы:**
1. Backend добавляет задачу в очередь через `LPUSH`
2. Воркеры (Telegram бот, Email сервис) получают задачи через `BRPOP`
3. Задачи обрабатываются асинхронно

#### 4. Telegram Bot (Отдельный контейнер)

**Назначение:**
- Принимает команды от пользователей в Telegram
- Получает задачи уведомлений из Redis
- Отправляет уведомления пользователям

**Команды:**
- `/start` - регистрация/приветствие, сохранение chat_id
- `/settings` - настройки уведомлений
- `/notifications` - управление уведомлениями

**Принцип работы:**
1. Пользователь отправляет `/start` боту
2. Бот сохраняет chat_id в БД
3. Backend отправляет уведомления в Redis Queue
4. Telegram бот получает задачи и отправляет сообщения

#### 5. Trading Bots (Торговые боты)

**Архитектура:**

Каждый тип бота работает в отдельном контейнере:
- Grid Bot - сеточная торговля
- DCA Bot - усреднение позиции
- Custom Bot - кастомные стратегии

**Принцип работы:**
1. Backend отправляет команду боту через Redis
2. Бот загружает конфигурацию из БД
3. Бот расшифровывает API ключи
4. Бот выполняет торговую стратегию
5. Бот обновляет статус в БД
6. Бот отправляет уведомления о событиях

### Потоки данных

#### Поток 1: Создание и запуск бота

```
1. Пользователь → POST /api/bots
   {
     "name": "My Bot",
     "exchange": "binance",
     "strategy": "grid",
     "api_key": "...",
     "api_secret": "..."
   }

2. Backend:
   - Валидирует данные
   - Шифрует API ключи
   - Сохраняет в БД
   - Отправляет команду в Redis Queue

3. Trading Bot:
   - Получает команду из Redis
   - Загружает конфигурацию из БД
   - Инициализирует стратегию
   - Начинает работу

4. Backend → Уведомление:
   - Отправляет в notification_queue
   - Telegram бот отправляет сообщение пользователю
```

#### Поток 2: Выставление ордера

```
1. Пользователь → POST /api/orders
   {
     "bot_id": 1,
     "symbol": "BTC/USDT",
     "side": "buy",
     "type": "limit",
     "quantity": 0.001,
     "price": 50000
   }

2. Backend:
   - Проверяет права доступа
   - Получает бота из БД
   - Расшифровывает API ключи
   - Вызывает ccxt для создания ордера на бирже

3. Биржа:
   - Создает ордер
   - Возвращает order_id

4. Backend:
   - Сохраняет ордер в БД
   - Добавляет в order_monitoring_queue
   - Отправляет уведомление

5. Order Monitor Worker:
   - Периодически проверяет статус ордера
   - Обновляет статус в БД
   - Отправляет уведомления при изменении
```

#### Поток 3: Система уведомлений

```
1. Событие в системе (например, ордер исполнен)

2. NotificationService:
   - Получает настройки пользователя из БД
   - Проверяет включенные каналы (email, telegram)
   - Формирует сообщение

3. Для Email:
   - Отправка через SMTP напрямую

4. Для Telegram:
   - Добавление задачи в notification_queue
   - Telegram бот получает задачу
   - Отправка сообщения через Telegram Bot API
```

### Принципы архитектуры

1. **Микросервисная архитектура**: Каждый компонент работает в отдельном контейнере
2. **Асинхронная обработка**: Использование Redis Queue для фоновых задач
3. **Безопасность**: Шифрование API ключей, JWT аутентификация
4. **Масштабируемость**: Возможность запуска нескольких экземпляров каждого сервиса
5. **Изоляция**: Падение одного компонента не влияет на другие
6. **Единая точка входа**: FastAPI Backend как центральный координатор

## Технологический стек

- **Backend**: FastAPI (Python 3.11+)
- **База данных**: PostgreSQL
- **Кеш/Очереди**: Redis
- **Контейнеризация**: Docker + Docker Compose
- **ORM**: SQLAlchemy
- **Аутентификация**: JWT токены
- **Валидация**: Pydantic
- **API клиенты**: ccxt (универсальная библиотека для криптобирж)
- **Документация API**: Swagger/OpenAPI (автоматически генерируется FastAPI)
- **Логирование**: Python logging + structlog (структурированные логи)
- **Email**: aiosmtplib или fastapi-mail для отправки email
- **Telegram**: python-telegram-bot или aiogram для Telegram бота

## Структура проекта

```
trading-bot-system/
├── backend/                     # FastAPI бэкенд (API сервер)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Точка входа FastAPI
│   │   ├── config.py            # Конфигурация приложения
│   │   ├── database.py          # Подключение к БД
│   │   ├── models/              # SQLAlchemy модели
│   │   │   ├── user.py
│   │   │   ├── bot.py
│   │   │   ├── order.py
│   │   │   └── notification_settings.py
│   │   ├── schemas/             # Pydantic схемы
│   │   │   ├── user.py
│   │   │   ├── bot.py
│   │   │   ├── order.py
│   │   │   └── notification.py
│   │   ├── api/                 # API роуты
│   │   │   ├── auth.py
│   │   │   ├── bots.py
│   │   │   ├── orders.py
│   │   │   └── notifications.py
│   │   ├── services/            # Бизнес-логика
│   │   │   ├── auth_service.py
│   │   │   ├── bot_service.py
│   │   │   ├── exchange_service.py
│   │   │   ├── order_service.py
│   │   │   └── notification_service.py
│   │   ├── core/                # Ядро системы
│   │   │   ├── security.py      # JWT, хеширование паролей
│   │   │   └── dependencies.py  # FastAPI dependencies
│   │   └── utils/
│   │       └── validators.py
│   ├── alembic/                 # Миграции БД
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── telegram-bot/                # Telegram бот (отдельный контейнер)
│   ├── bot.py                   # Основной файл бота
│   ├── handlers/                # Обработчики команд
│   │   ├── __init__.py
│   │   ├── start.py
│   │   ├── notifications.py
│   │   └── settings.py
│   ├── services/                # Сервисы бота
│   │   ├── message_service.py
│   │   └── user_service.py
│   ├── utils/
│   │   ├── database.py          # Подключение к БД
│   │   └── redis_client.py     # Подключение к Redis
│   ├── main.py                  # Точка входа
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── bots/                        # Отдельные боты (каждый в своем контейнере)
│   ├── base/                    # Базовый класс и общая логика
│   │   ├── __init__.py
│   │   ├── bot_base.py          # Абстрактный базовый класс бота
│   │   ├── exchange_client.py   # Общая логика работы с биржами
│   │   └── database.py          # Подключение к БД
│   │
│   ├── grid_bot/                # Grid бот (пример)
│   │   ├── __init__.py
│   │   ├── grid_bot.py          # Логика Grid стратегии
│   │   ├── main.py              # Точка входа для контейнера
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── dca_bot/                 # DCA бот (пример)
│   │   ├── __init__.py
│   │   ├── dca_bot.py           # Логика DCA стратегии
│   │   ├── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── custom_bot/              # Шаблон для создания нового бота
│       ├── __init__.py
│       ├── custom_bot.py       # Логика кастомной стратегии
│       ├── main.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── docker-compose.yml            # Оркестрация всех сервисов
├── .env.example                  # Пример переменных окружения
└── README.md
```

## Основные компоненты

### 1. Система аутентификации

- Регистрация пользователей
- JWT аутентификация
- Хеширование паролей (bcrypt)
- Middleware для защиты роутов

### 2. Управление ботами

- Создание бота с параметрами (стратегия, пара, тип ордера)
- Сохранение API ключей биржи (зашифровано)
- Управление жизненным циклом бота (активен/остановлен) через Redis
- Отправка команд ботам через Redis Queue
- История операций бота

### 3. Система ордеров

- Выставление ордеров через API биржи
- Отслеживание статуса ордеров (Redis + фоновые воркеры)
- Автоматические действия при изменении статуса
- Логирование всех операций

### 4. Интеграция с биржами

- Унифицированный интерфейс для Binance, Bybit, OKX и Bitget через ccxt
- Обработка ошибок API
- Rate limiting
- WebSocket для real-time обновлений (опционально)

### 5. Система уведомлений

- Telegram бот в отдельном контейнере
- Email сервис для отправки уведомлений
- Настройки уведомлений пользователей (каналы, типы событий)
- Асинхронная отправка через Redis Queue
- Типы событий: создание/остановка бота, ордеры, ошибки, достижение целей

## Реализация

### Этап 1: Базовая инфраструктура

- Настройка Docker Compose (PostgreSQL, Redis, FastAPI Backend)
- Конфигурация проекта (settings, env variables)
- Базовая структура FastAPI приложения
- Настройка Swagger/OpenAPI документации (автоматически доступна на `/docs` и `/redoc`)
- Подключение к БД (SQLAlchemy)
- Создание базовой структуры для ботов (папка `bots/base/`) - только заглушки

### Этап 2: Аутентификация

- Модели User (SQLAlchemy)
- Схемы для регистрации/логина (Pydantic)
- JWT генерация и валидация
- Роуты `/auth/register`, `/auth/login`, `/auth/me`
- Защита роутов через dependencies

### Этап 3: Модели данных

- Модель Bot (user_id, exchange, strategy, params, status, api_keys_encrypted)
- Модель Order (bot_id, exchange_order_id, symbol, side, type, status, price, quantity)
- Модель BotConfig (настройки стратегии)
- Модель NotificationSettings (user_id, email, telegram_chat_id, enabled_channels, event_types)
- Миграции Alembic

### Этап 4: Интеграция с биржами

- Обёртка для ccxt (Binance/Bybit/OKX/Bitget клиенты)
- Сервис для работы с биржами (выставление ордеров, получение статуса)
- Шифрование API ключей пользователей
- Валидация параметров ордеров

### Этап 5: Управление ботами

- API для создания/обновления/удаления ботов
- Валидация параметров бота
- Сохранение конфигурации в БД
- Роуты `/api/bots` (CRUD операции)
- Документация всех endpoints в Swagger с примерами запросов/ответов

### Этап 6: Архитектура ботов (отдельные контейнеры) - ЗАГЛУШКИ

- Создание структуры папок для ботов (`bots/base/`, `bots/grid_bot/`)
- Заглушки базового класса бота (`bots/base/bot_base.py`) - только интерфейс
- Заглушка общей логики работы с биржами (`bots/base/exchange_client.py`) - только структура
- Заглушка подключения ботов к БД и Redis - только конфигурация
- Заглушка примера Grid бота - только структура файлов и Dockerfile
- **Примечание**: Полная реализация ботов будет добавлена позже, сейчас только архитектурные заглушки

### Этап 7: Система ордеров

- Выставление ордеров через бота
- Сохранение ордеров в БД
- Добавление задач в Redis Queue для мониторинга
- Отслеживание статусов ордеров внутри ботов
- Автоматические действия при изменении статуса

### Этап 8: Мониторинг и логирование

- Настройка структурированного логирования (structlog)
- Логирование всех операций (создание ботов, ордеры, ошибки API)
- Ротация логов (logrotate или Python logging.handlers)
- Endpoint для получения истории ордеров
- Статистика по ботам
- Health check endpoints

### Этап 9: Система уведомлений

- Модель NotificationSettings в БД
- Email сервис (aiosmtplib/fastapi-mail) с настройками SMTP
- Notification Service в бэкенде для отправки задач в Redis Queue
- Telegram бот в отдельном контейнере:
                                                                - Обработчики команд (/start, /settings, /notifications)
                                                                - Получение задач из Redis Queue
                                                                - Отправка уведомлений пользователям
                                                                - Сохранение telegram_chat_id при регистрации
- API для управления настройками уведомлений
- Интеграция уведомлений в события системы (создание ботов, ордеры, ошибки)

## Архитектура ботов (отдельные контейнеры)

### Принцип работы

Каждый тип бота работает в **отдельном Docker контейнере**:

1. **Бэкенд API** управляет ботами через БД и Redis
2. **Боты** подключаются к общей БД и Redis
3. **Координация** через Redis Queue:

                                                                                                - Бэкенд отправляет команды ботам через Redis
                                                                                                - Боты получают задачи и выполняют свою логику
                                                                                                - Боты обновляют статус в БД

### Преимущества

- **Изоляция**: падение одного бота не влияет на другие
- **Масштабируемость**: можно запускать несколько экземпляров одного типа
- **Независимое развертывание**: обновление одного бота не затрагивает остальные
- **Разные зависимости**: каждый бот может иметь свои библиотеки
- **Удобная отладка**: логи каждого бота отдельно

## Система уведомлений

### Архитектура

```mermaid
graph TB
    Event[Событие системы] --> NotificationService[Notification Service]
    NotificationService --> Redis[Redis Queue]
    Redis --> TelegramBot[Telegram Bot Container]
    Redis --> EmailWorker[Email Worker]
    
    TelegramBot --> TelegramAPI[Telegram Bot API]
    EmailWorker --> SMTP[SMTP Server]
    
    UserSettings[(User Settings)] --> NotificationService
    TelegramBot --> UserSettings
```

### Компоненты

1. **Notification Service** (в бэкенде):

                                                                                                - Единый интерфейс для отправки уведомлений
                                                                                                - Получение настроек пользователя из БД
                                                                                                - Добавление задач в Redis Queue

2. **Email Service**:

                                                                                                - Отправка email через SMTP (Gmail, SendGrid, Mailgun)
                                                                                                - HTML и текстовые шаблоны
                                                                                                - Обработка ошибок отправки

3. **Telegram Bot** (отдельный контейнер):

                                                                                                - Обработка команд пользователей
                                                                                                - Получение задач из Redis Queue
                                                                                                - Отправка уведомлений через Telegram Bot API
                                                                                                - Сохранение chat_id пользователей

4. **Notification Settings**:

                                                                                                - Email адрес пользователя
                                                                                                - Telegram chat_id
                                                                                                - Включенные каналы уведомлений (email, telegram)
                                                                                                - Типы событий для уведомлений

### Типы событий

- `bot_created` - создан новый бот
- `bot_stopped` - бот остановлен
- `order_placed` - выставлен ордер
- `order_filled` - ордер исполнен
- `order_cancelled` - ордер отменен
- `exchange_error` - ошибка при работе с биржей
- `bot_error` - критическая ошибка бота
- `target_reached` - достигнут целевой уровень

### Docker Compose структура

```yaml
services:
  # Бэкенд API
  backend:
    build: ./backend
    ports:
   - "8000:8000"
    environment:
   - DATABASE_URL=postgresql://user:pass@postgres:5432/db
   - REDIS_URL=redis://redis:6379
   - SMTP_HOST=smtp.gmail.com
   - SMTP_PORT=587
   - SMTP_USER=${SMTP_USER}
   - SMTP_PASSWORD=${SMTP_PASSWORD}
    depends_on:
   - postgres
   - redis

  # Telegram бот
  telegram-bot:
    build: ./telegram-bot
    environment:
   - DATABASE_URL=postgresql://user:pass@postgres:5432/db
   - REDIS_URL=redis://redis:6379
   - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    depends_on:
   - postgres
   - redis
    restart: unless-stopped

  # База данных
  postgres:
    image: postgres:15
    # ... конфигурация

  # Redis
  redis:
    image: redis:7-alpine
    # ... конфигурация

  # Grid бот (пример)
  grid-bot:
    build: ./bots/grid_bot
    environment:
   - DATABASE_URL=postgresql://user:pass@postgres:5432/db
   - REDIS_URL=redis://redis:6379
   - BOT_TYPE=grid
    depends_on:
   - postgres
   - redis
    restart: unless-stopped
```

### Команды управления

```bash
# Запустить все сервисы
docker-compose up -d

# Запустить только Telegram бот
docker-compose up -d telegram-bot

# Логи Telegram бота
docker-compose logs -f telegram-bot

# Перезапустить Telegram бот
docker-compose restart telegram-bot
```

## Файлы для создания

### Backend

1. `backend/Dockerfile` - образ FastAPI приложения
2. `backend/requirements.txt` - зависимости Python
3. `backend/app/main.py` - FastAPI приложение с настройкой Swagger
4. `backend/app/config.py` - настройки
5. `backend/app/database.py` - подключение к БД
6. `backend/app/models/notification_settings.py` - модель настроек уведомлений
7. `backend/app/services/notification_service.py` - сервис уведомлений
8. Модели, схемы, сервисы, API роуты (см. структуру выше)

### Telegram Bot

9. `telegram-bot/Dockerfile` - образ Telegram бота
10. `telegram-bot/requirements.txt` - зависимости (python-telegram-bot или aiogram)
11. `telegram-bot/main.py` - точка входа бота
12. `telegram-bot/bot.py` - основной класс бота
13. `telegram-bot/handlers/` - обработчики команд
14. `telegram-bot/services/message_service.py` - сервис отправки сообщений

### Боты (заглушки)

15. `bots/base/bot_base.py` - заглушка базового класса бота (только интерфейс)
16. `bots/base/exchange_client.py` - заглушка общей логики работы с биржами (только структура)
17. `bots/grid_bot/grid_bot.py` - заглушка Grid бота (только структура класса)
18. `bots/grid_bot/main.py` - заглушка точки входа для контейнера
19. `bots/grid_bot/Dockerfile` - образ Grid бота (базовая структура)
20. `bots/grid_bot/requirements.txt` - минимальные зависимости

### Инфраструктура

21. `docker-compose.yml` - оркестрация всех сервисов
22. `.env.example` - пример конфигурации

## Swagger/OpenAPI документация

FastAPI автоматически генерирует интерактивную документацию API:

- **Swagger UI**: доступна по адресу `/docs` (интерактивный интерфейс для тестирования API)
- **ReDoc**: доступна по адресу `/redoc` (альтернативный формат документации)
- **OpenAPI схема**: доступна по адресу `/openapi.json`

Настройка включает:

- Метаданные API (название, версия, описание)
- Теги для группировки endpoints
- Примеры запросов и ответов в Pydantic схемах
- Описания параметров и моделей данных
- Автоматическая валидация через Pydantic схемы
- JWT аутентификация в Swagger UI (кнопка "Authorize")

## Логирование и просмотр логов

### Где смотреть логи

#### 1. Логи Docker контейнеров (основной способ)

**Просмотр логов всех сервисов:**

```bash
docker-compose logs
```

**Просмотр логов конкретного сервиса:**

```bash
docker-compose logs backend        # Логи FastAPI приложения
docker-compose logs telegram-bot   # Логи Telegram бота
docker-compose logs postgres       # Логи PostgreSQL
docker-compose logs redis          # Логи Redis
docker-compose logs grid-bot       # Логи Grid бота
```

**Следить за логами в реальном времени:**

```bash
docker-compose logs -f telegram-bot
```

## Безопасность

- Шифрование API ключей бирж (AES)
- JWT токены с истечением срока
- Валидация всех входных данных
- Rate limiting для API
- HTTPS в продакшене
- Безопасное хранение Telegram Bot Token и SMTP credentials

## Дальнейшее развитие

- WebSocket для real-time обновлений
- Поддержка дополнительных бирж
- Более сложные стратегии торговли
- Backtesting
- Dashboard для мониторинга
- Push-уведомления через Firebase/APNs
