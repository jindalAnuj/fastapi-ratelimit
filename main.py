import redis.asyncio as redis
import uvicorn
from fastapi import Depends, FastAPI, Request

from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

app = FastAPI()

async def default_identifier(request: Request):
    forwarded = request.headers.get("X-Bot-ID")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host + ":" + request.scope["path"]

@app.on_event("startup")
async def startup():
    redis_connection = redis.from_url("redis://127.0.0.1", encoding="utf-8", decode_responses=True)

    await FastAPILimiter.init(redis_connection)


@app.get("/", dependencies=[Depends(RateLimiter(times=2, seconds=15))])
async def index():
    return {"msg": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("main:app", debug=True, reload=True)