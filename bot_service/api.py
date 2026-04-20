import os
import aiohttp

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


async def api_get(endpoint: str, params: dict):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=aiohttp.ClientTimeout(total=15)) as res:
            return await res.json()


async def api_post(endpoint: str, payload: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_BASE_URL}{endpoint}", json=payload, timeout=aiohttp.ClientTimeout(total=15)) as res:
            return await res.json()
