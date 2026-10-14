from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from sqlalchemy import text

from app.config import get_settings
from app.db import engine
from app.exceptions import AuthenticationError, UnprocessableError
from app.routers import auth, calls, campaigns, stats
from app.services.broadcaster import Broadcaster


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis.from_url(get_settings().redis_url)
    app.state.broadcaster = Broadcaster(redis)
    await app.state.broadcaster.start()
    yield
    await app.state.broadcaster.stop()
    await redis.aclose()
    await engine.dispose()


app = FastAPI(title="Call Analytics API", version="0.1.0", lifespan=lifespan)
for router in (auth.router, campaigns.router, calls.router, stats.router):
    app.include_router(router)


@app.exception_handler(UnprocessableError)
async def unprocessable(request: Request, error: UnprocessableError) -> JSONResponse:
    return JSONResponse({"detail": str(error)}, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)


@app.exception_handler(AuthenticationError)
async def unauthenticated(request: Request, error: AuthenticationError) -> JSONResponse:
    return JSONResponse({"detail": str(error)}, status_code=status.HTTP_401_UNAUTHORIZED)


@app.get("/api/health", tags=["health"])
async def health() -> dict:
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
    return {"status": "ok"}
