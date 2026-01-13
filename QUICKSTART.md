# Быстрый старт

## Пошаговая инструкция

### 1. Подготовка

Убедитесь, что у вас установлены:
- Docker Desktop (Windows/Mac) или Docker + Docker Compose (Linux)
- Git (опционально)

### 2. Создание файла .env

Создайте файл `.env` в корне проекта:

**Windows PowerShell:**
```powershell
Copy-Item .env.example .env
notepad .env
```

**Linux/Mac:**
```bash
cp .env.example .env
nano .env
```

### 3. Настройка переменных

Откройте `.env` и укажите:

**Обязательные:**
- `SECRET_KEY` - сгенерируйте случайную строку (можно использовать: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `TELEGRAM_BOT_TOKEN` - получите у @BotFather в Telegram

**Опциональные (для email):**
- `SMTP_USER` - ваш email
- `SMTP_PASSWORD` - пароль приложения (для Gmail нужен App Password)

### 4. Запуск

```bash
docker-compose up -d
```

### 5. Проверка

Откройте в браузере:
- http://localhost:8000/docs - Swagger UI
- http://localhost:8000/health - проверка здоровья

### 6. Просмотр логов

```bash
# Все логи
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f telegram-bot
docker-compose logs -f postgres
docker-compose logs -f redis
```

### 7. Остановка

```bash
docker-compose down
```

### 8. Полная очистка (удаление данных)

```bash
docker-compose down -v
```

## Первое использование API

### Регистрация пользователя

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_password"
  }'
```

### Вход

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_password"
  }'
```

Ответ содержит `access_token` - используйте его для авторизации.

### Использование токена

```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Настройка Telegram бота

1. Создайте бота через @BotFather в Telegram
2. Получите токен
3. Добавьте токен в `.env` как `TELEGRAM_BOT_TOKEN`
4. Перезапустите: `docker-compose restart telegram-bot`
5. Найдите вашего бота в Telegram и отправьте `/start`

## Решение проблем

### Порт уже занят

Измените порты в `.env`:
```
BACKEND_PORT=8001
POSTGRES_PORT=5433
REDIS_PORT=6380
```

### Ошибки при сборке

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Проблемы с БД

```bash
docker-compose exec postgres psql -U trading_user -d trading_bot_db
```

### Просмотр статуса контейнеров

```bash
docker-compose ps
```
