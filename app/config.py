from dotenv import load_dotenv
import os

load_dotenv()
BASE_DIR = os.getenv("BASE_DIR", os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = f'{BASE_DIR}/statics_files'
UPLOAD_DIR = f'{STATIC_DIR}/uploads'
PDF_DIR = f'{STATIC_DIR}/pdfs'
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
SENTRY_DSN = os.getenv("SENTRY_DSN", "") # Опционально
MAX_FILE_SIZE_MB = os.getenv("MAX_FILE_SIZE_MB", 100) # 100 MB