from fastapi import Request, HTTPException
from dotenv import load_dotenv
import os
load_dotenv()

API_KEY = os.getenv("API_KEY")

async def verify_api_key(request: Request):
    api_key = request.headers.get("X-API-Key")
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

