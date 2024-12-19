import logging

import sentry_sdk
from fastapi import FastAPI, Request
from prometheus_fastapi_instrumentator import Instrumentator

from app.api import api_route
from app.config import SENTRY_DSN
from app.logging_config import setup_logging
from app.middleware import SessionIDMiddleware
from app.utils.systems import check_mysql_connection, check_redis_connection

setup_logging()
logger = logging.getLogger(__name__)

if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=1.0)
    logger.info("✅ Sentry initialized")
else:
    logger.warning("⚠️ Sentry DSN not provided. Sentry is disabled.")

app = FastAPI(title="File Conversion Service", version="1.0.0")
app.add_middleware(SessionIDMiddleware)

if not check_mysql_connection() or not check_redis_connection():
    import sys
    logger.error("🚫 Service startup aborted. Check database and Redis connections.")
    sys.exit(1)

logger.info("✅ All dependencies are available. Service starting...")
app.include_router(api_route)

Instrumentator().instrument(app).expose(app) # Prometheus

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Логирует запросы и ответы"""
    logger.info(f"➡️ Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"⬅️ Response: {response.status_code}")
    return response

