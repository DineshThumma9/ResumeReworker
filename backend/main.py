import logging
import os
from contextlib import asynccontextmanager

import redis.asyncio as redis
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter

from api.routes import router
from core.config import settings
from core.database import create_tables
from utils.http_client import close_http_client

load_dotenv()

if settings.langchain_tracing_v2.lower() == "true":
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
    if settings.langchain_api_key:
        os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables and initialize redis on startup."""
    await create_tables()
    try:
        redis_conn = redis.from_url(
            settings.redis_url, encoding="utf-8", decode_responses=True
        )
        await FastAPILimiter.init(redis_conn)
        logger.info("Connected to Redis and initialized FastAPILimiter")
    except Exception as e:
        logger.error(f"Failed to initialize Redis/FastAPILimiter: {e}")
    yield
    try:
        if "redis_conn" in locals():
            await redis_conn.close()  # type: ignore
        await close_http_client()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


app = FastAPI(title="ResumeReworker API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.allowed_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/previews", exist_ok=True)
app.mount("/api/static", StaticFiles(directory="static"), name="static")

app.include_router(router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
