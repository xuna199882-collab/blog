# app/core/cache.py
import json
import redis
from app.core.config import settings

r = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def get_json(key: str):
    raw = r.get(key)
    return json.loads(raw) if raw else None


def set_json(key: str, value, expire: int = 300):
    r.setex(key, expire, json.dumps(value, ensure_ascii=False, default=str))


def delete(*keys: str):
    if keys:
        r.delete(*keys)