import os

import redis
from PIL import Image
from reportlab.pdfgen import canvas
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from app.config import DATABASE_URL, REDIS_URL, UPLOAD_DIR, PDF_DIR, BASE_DIR
from app.enams import FileExtensionEnum
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

def check_mysql_connection():
    """Проверяет подключение к MySQL."""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("✅ Successfully connected to MySQL")
        return True
    except OperationalError as e:
        logger.error(f"❌ Failed to connect to MySQL: {e}")
        return False


def check_redis_connection():
    """Проверяет подключение к Redis."""
    try:
        r = redis.from_url(REDIS_URL)
        r.ping()
        logger.info("✅ Successfully connected to Redis")
        return True
    except redis.ConnectionError as e:
        logger.error(f"❌ Failed to connect to Redis: {e}")
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
        msg = f"Input file '{file_path}' does not exist."
        logger.error(msg)
        raise FileNotFoundError(msg)

    try:
        # Конвертация изображений (png, bmp, jpg, jpeg)
        files_extensive = tuple((ext.value for ext in FileExtensionEnum if ext.value != "eps"))
        if input_path.lower().endswith(files_extensive):
            image = Image.open(file_path)
            image.convert("RGB").save(output_path, "PDF")
            logger.info(f"✅ Successfully converted image to PDF: {output_path}")

        # Конвертация EPS в PDF
        elif input_path.lower().endswith(FileExtensionEnum.EPS.value):
            with Image.open(file_path) as img:
                img.load()
            c = canvas.Canvas(output_path)
            c.drawImage(file_path, 0, 0)
            c.save()
            logger.info(f"✅ Successfully converted EPS to PDF: {output_path}")
        else:
            msg = "Unsupported file format for conversion."
            logger.error(msg)
            raise ValueError(msg)
    except Exception as e:
        msg = f"Error converting file to PDF: {e}"
        logger.error(msg)
        raise RuntimeError(msg)


def create_directories():
    """
    Создает директории для загрузки и сохранения PDF, если их нет.
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(PDF_DIR, exist_ok=True)
    logger.info(f"✅ Directories ensured: '{UPLOAD_DIR}' and '{PDF_DIR}'")


def get_absolute_path(relative_path: str) -> str:
    """
    Получить абсолютный путь для файла.
    :param relative_path: Относительный путь.
    :return: Абсолютный путь.
    """
    return os.path.join(BASE_DIR, relative_path)