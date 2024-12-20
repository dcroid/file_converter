from celery import Celery
from app.database import SessionLocal
from app.models import File, FileStatusEnum
from app.utils.systems import convert_to_pdf
from app.config import REDIS_URL
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

celery_app = Celery(
    "worker",
    backend=REDIS_URL,
    broker=REDIS_URL
)
celery_app.conf.task_routes = {"convert_to_pdf_task": {"queue": "file_task"}}
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
)

@celery_app.task(name="convert_to_pdf_task")
def convert_to_pdf_task(file_id: int, file_path: str, output_path: str):
    """Таска для конвертации файла в PDF."""
    db = SessionLocal()
    try:
        file = db.query(File).filter(File.id == file_id).first()
        if not file:
            logger.error("Файл с ID %d не найден", file_id)
            return

        logger.info("Начало выполнения задачи для файла ID: %d", file_id)
        convert_to_pdf(file_path, output_path)

        file.status = FileStatusEnum.PROCESSING
        file.pdf_path = output_path
        logger.info("Задача завершена успешно для файла ID: %d", file_id)
    except Exception as e:
        logger.error("Ошибка при выполнении задачи для файла ID %d: %s", file_id, e)
        if file:
            file.status = FileStatusEnum.ERROR
    finally:
        db.commit()
        db.close()