import redis.asyncio as redis

REDIS_HOST = "192.168.1.23"
REDIS_PORT = 6379

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

async def set_cache(key: str, value: str, expire_seconds: int = 3600):
    """设置缓存，默认1小时过期"""
    await redis_client.set(key, value, ex=expire_seconds)

async def get_cache(key: str):
    """获取缓存"""
    return await redis_client.get(key)
