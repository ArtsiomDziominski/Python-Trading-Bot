# Trading Bot System

Система для создания и управления торговыми ботами для Binance, Bybit, OKX и Bitget.

## Архитектура

- **Backend API** (FastAPI) - основной API сервер
- **Telegram Bot** - бот для уведомлений в отдельном контейнере
- **Trading Bots** - торговые боты в отдельных контейнерах (заглушки)
- **PostgreSQL** - база данных
- **Redis** - очереди и кеш

## Быстрый старт

### Шаг 1: Настройка переменных окружения

Создайте файл `.env` в корне проекта (скопируйте из `.env.example`):

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**Linux/Mac:**
```bash
cp .env.example .env
```

Затем откройте `.env` и заполните обязательные переменные:
- `SECRET_KEY` - сгенерируйте случайную строку (минимум 32 символа)
- `TELEGRAM_BOT_TOKEN` - токен вашего Telegram бота (получите у @BotFather)
- `SMTP_USER` и `SMTP_PASSWORD` - для отправки email (опционально)

### Шаг 2: Запуск проекта

**Запустить все сервисы:**
```bash
docker-compose up -d
```

**Запустить с просмотром логов:**
```bash
docker-compose up
```

**Остановить все сервисы:**
```bash
docker-compose down
```

**Пересобрать контейнеры после изменений:**
```bash
docker-compose up -d --build
```

### Шаг 3: Проверка работы

1. **API доступен по адресу:** http://localhost:8000
2. **Swagger документация:** http://localhost:8000/docs
3. **ReDoc документация:** http://localhost:8000/redoc
4. **Health check:** http://localhost:8000/health

### Шаг 4: Первый запуск

После первого запуска выполните миграции БД (если нужно):
```bash
docker-compose exec backend alembic upgrade head
```

Или таблицы создадутся автоматически при первом запуске (через `Base.metadata.create_all`).

## Структура проекта

```
trading-bot-system/
├── backend/          # FastAPI бэкенд
├── telegram-bot/     # Telegram бот
├── bots/             # Торговые боты (заглушки)
└── docker-compose.yml
```

## API Endpoints

### Аутентификация
- `POST /api/auth/register` - регистрация
- `POST /api/auth/login` - вход
- `GET /api/auth/me` - текущий пользователь

### Боты
- `POST /api/bots` - создать бота
- `GET /api/bots` - список ботов
- `GET /api/bots/{id}` - получить бота
- `PUT /api/bots/{id}` - обновить бота
- `DELETE /api/bots/{id}` - удалить бота

### Ордеры
- `POST /api/orders` - создать ордер
- `GET /api/orders` - список ордеров
- `GET /api/orders/{id}` - получить ордер

### Уведомления
- `GET /api/notifications/settings` - настройки уведомлений
- `POST /api/notifications/settings` - создать настройки
- `PUT /api/notifications/settings` - обновить настройки

### Статистика
- `GET /api/stats/stats` - статистика
- `GET /api/stats/history` - история ордеров

## Переменные окружения

См. `.env.example` для полного списка переменных.

## Логи

Просмотр логов:
```bash
docker-compose logs -f backend
docker-compose logs -f telegram-bot
```

## Разработка

Для разработки с hot-reload:
```bash
docker-compose up
```

Файлы монтируются как volumes, изменения применяются автоматически.

## Подробная документация

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - подробное описание архитектуры и принципов работы системы
- **[QUICKSTART.md](QUICKSTART.md)** - пошаговая инструкция по запуску и использованию
- **[DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)** - план разработки проекта с описанием всех этапов и компонентов