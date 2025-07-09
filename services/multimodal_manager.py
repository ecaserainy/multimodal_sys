import asyncio
from services.cache import set_cache, get_cache
from services.queue_manager import add_task

async def run_model_inference(input_data: str) -> str:

    await asyncio.sleep(5)
    return f"推理结果: {input_data[::-1]}"

async def cache_model_result(cache_key: str, input_data: str):
    result = await run_model_inference(input_data)
    await set_cache(cache_key, result, expire_seconds=3600)

async def infer_with_cache(input_data: str) -> str:
    cache_key = f"model_result:{input_data}"

    cached_result = await get_cache(cache_key)
    if cached_result:
        return cached_result

    add_task(cache_model_result, cache_key, input_data)
    return "结果正在生成中，请稍后重试"

