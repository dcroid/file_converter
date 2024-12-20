import os

import redis
from PIL import Image
from reportlab.pdfgen import canvas
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from app.config import DATABASE_URL, REDIS_URL, UPLOAD_DIR, PDF_DIR, BASE_DIR
from app.enums import FileExtensionEnum, LogMessageEnum
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

redis_client = None

def get_redis_client() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(REDIS_URL)
    return redis_client

def check_mysql_connection() -> bool:
    """Проверяет подключение к MySQL."""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info(LogMessageEnum.SUCCESSFUL_CHECK.value.format("MySQL"))
        return True
    except OperationalError as e:
        logger.error(LogMessageEnum.FAILED_CHECK.value.format("MySQL", e))
        return False


def check_redis_connection() -> bool:
    """Проверяет подключение к Redis."""
    try:
        r = get_redis_client()
        r.ping()
        logger.info(LogMessageEnum.SUCCESSFUL_CHECK.value.format("Redis"))
        return True
    except redis.ConnectionError as e:
        logger.error(LogMessageEnum.FAILED_CHECK.value.format("Redis", e))
        return False


def validate_file_extension(extension: str) -> bool:
    """Проверка расширения файла с использованием FileExtensionEnum."""
    return extension[1:].lower() in {ext.value for ext in FileExtensionEnum}


def convert_to_pdf(input_path: str, output_path: str):
    """
    Конвертирует изображение (png, bmp, jpg, jpeg, eps) в PDF.
    """
    file_path = get_absolute_path(input_path)
    output_path = get_absolute_path(output_path)
    if not os.path.exists(file_path):
        logger.error(LogMessageEnum.FILE_NOT_EXIST.value.format(file_path))
        raise FileNotFoundError(LogMessageEnum.FILE_NOT_EXIST.value.format(file_path))

    try:
        # Конвертация изображений (png, bmp, jpg, jpeg)
        files_extensive = tuple(
            (
                ext.value for ext in FileExtensionEnum if ext.value != FileExtensionEnum.EPS.value
            )
        )
        if input_path.lower().endswith(files_extensive):
            image = Image.open(file_path)
            image.convert("RGB").save(output_path, "PDF")
            logger.info(LogMessageEnum.SUCCESSFUL_CONVERT.value.format("image", output_path))

        # Конвертация EPS в PDF
        elif input_path.lower().endswith(FileExtensionEnum.EPS.value):
            with Image.open(file_path) as img:
                img.load()
            c = canvas.Canvas(output_path)
            c.drawImage(file_path, 0, 0)
            c.save()
            logger.info(LogMessageEnum.SUCCESSFUL_CONVERT.value.format(FileExtensionEnum.EPS.value, output_path))
        else:
            logger.error(LogMessageEnum.UNSUPPORTED_FORMAT.value)
            raise ValueError(LogMessageEnum.UNSUPPORTED_FORMAT.value)
    except Exception as e:
        logger.error(LogMessageEnum.FAILED_CONVERT.value.format(e))
        raise RuntimeError(LogMessageEnum.FAILED_CONVERT.value.format(e))


def create_directories():
    """
    Создает директории для загрузки и сохранения PDF, если их нет.
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(PDF_DIR, exist_ok=True)
    logger.info(LogMessageEnum.DIRECTORIES_ENSURED.value.format(UPLOAD_DIR, PDF_DIR))


def get_absolute_path(relative_path: str) -> str:
    """
    Получить абсолютный путь для файла.
    :param relative_path: Относительный путь.
    :return: Абсолютный путь.
    """
    return os.path.join(BASE_DIR, relative_path)