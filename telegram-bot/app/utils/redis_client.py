import redis
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

def get_redis() -> redis.Redis:
    return redis.from_url(REDIS_URL)
