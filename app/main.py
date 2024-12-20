import logging
import sys

import sentry_sdk
from fastapi import FastAPI, Request
from prometheus_fastapi_instrumentator import Instrumentator

from app.api import api_route
from app.config import SENTRY_DSN, SERVICE_NAME, SERVICE_VERSION
from app.enums import LogMessageEnum
from app.logging_config import setup_logging
from app.middleware import SessionIDMiddleware
from app.utils.systems import check_mysql_connection, check_redis_connection

setup_logging()
logger = logging.getLogger(__name__)

def initialize_sentry() -> None:
    """Инициализация Sentry SDK для мониторинга ошибок."""
    if SENTRY_DSN:
        sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=1.0)
        logger.info(LogMessageEnum.SENTRY_INITIALIZED.value)
    else:
        logger.warning(LogMessageEnum.SENTRY_DSN_NOT_PROVIDED.value)

def check_dependencies() -> None:
    """Проверяет доступность MySQL и Redis перед запуском сервиса."""
    if not check_mysql_connection() or not check_redis_connection():
        logger.error(LogMessageEnum.SERVICE_STARTUP_ABORTED.value)
        sys.exit(1)


# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)

# Инициализация Sentry
initialize_sentry()

app = FastAPI(title=SERVICE_NAME, version=SERVICE_VERSION)
app.add_middleware(SessionIDMiddleware)

check_dependencies()
app.include_router(api_route) # API routes
Instrumentator().instrument(app).expose(app) # Prometheus
logger.info(LogMessageEnum.ALL_DEPENDENCIES_AVAILABLE.value)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Логирует запросы и ответы"""
    logger.info(LogMessageEnum.REQUEST.value.format(request_method=request.method, request_url=request.url))
    response = await call_next(request)
    logger.info(LogMessageEnum.RESPONSE.value.format(response_status_code=response.status_code))
    return response
