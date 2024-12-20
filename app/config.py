from dotenv import load_dotenv
import os

load_dotenv()

# Дериктории для файлов
BASE_DIR = os.getenv("BASE_DIR", os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = f'{BASE_DIR}/statics_files'
UPLOAD_DIR = f'{STATIC_DIR}/uploads'
PDF_DIR = f'{STATIC_DIR}/pdfs'

# Основной URL
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# MySQL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")

POOL_SIZE = os.getenv("POOL_SIZE", 10)  # Максимальное количество соединений в пуле
MAX_OVERFLOW = os.getenv("MAX_OVERFLOW", 20)    # Максимальное количество дополнительных соединений
POOL_TIMEOUT = os.getenv("POOL_TIMEOUT", 30)    # Время ожидания соединения

# Redis
REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    raise ValueError("REDIS_URL is not set in environment variables")

# Sentry
SENTRY_DSN = os.getenv("SENTRY_DSN", "") # Опционально

# Максимальный размер файла
MAX_FILE_SIZE_MB = os.getenv("MAX_FILE_SIZE_MB", 100) # 100 MB