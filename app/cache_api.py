from fastapi import APIRouter, HTTPException
from services.cache import set_cache, get_cache
from services.multimodal_manager import infer_with_cache

router = APIRouter()

@router.get("/model/infer")
async def model_infer(input: str):
    result = await infer_with_cache(input)
    return {"input": input, "result": result}

@router.get("/cache/set")
async def cache_set(key: str, value: str):
    await set_cache(key, value)
    return {"msg": f"Cache set: {key} = {value}"}

@router.get("/cache/get")
async def cache_get(key: str):
    value = await get_cache(key)
    if value is None:
        raise HTTPException(status_code=404, detail="Cache key not found")
    return {"key": key, "value": value}
