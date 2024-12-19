import os
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, Depends, Request
from sqlalchemy.orm import Session

from app.config import MAX_FILE_SIZE_MB, UPLOAD_DIR, PDF_DIR
from app.context import session_id_context
from app.database import get_db
from app.enums import FileStatusEnum, FileTypeInSystemEnum
from app.models import File, Session as SessionModel
from app.schemas import FileResponse as ApiFileResponse
from app.utils.file_handler import download_file
from app.utils.systems import validate_file_extension
from app.celery_worker import convert_to_pdf_task

router = APIRouter()

@router.post("/upload/")
async def upload_file(file: UploadFile, db: Session = Depends(get_db)):
    # Проверка сессии
    session_id = session_id_context.get()
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    session.last_login = datetime.utcnow()
    db.commit()

    # Проверка размера файла
    contents = await file.read()
    file_size = len(contents)
    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 100 MB)")

    file_name, file_extension = os.path.splitext(file.filename)

    # Проверка расширения файла
    if not validate_file_extension(file_extension):
        raise HTTPException(status_code=400, detail="Invalid file type")

    file_name = f"{str(uuid.uuid4())}_{file_name}"
    full_file_name = f"{file_name}{file_extension}"
    filepath = f"{UPLOAD_DIR}/{full_file_name}"
    with open(filepath, "wb") as f:
        f.write(contents)

    new_file = File(
        session_id=session_id,
        filename=full_file_name,
        filepath=filepath,
        size=file_size,
        extension=file_extension,
        status=FileStatusEnum.uploaded,
    ).save(db)

    pdf_path = f"{PDF_DIR}/{file_name}.pdf"

    convert_to_pdf_task.delay(new_file.id, filepath, pdf_path)

    return {"id": new_file.id, "status": new_file.status.value}


@router.get("/files/", response_model=list[ApiFileResponse])
def get_files(request: Request = None, db: Session = Depends(get_db)):
    """
    Получение файлов только для указанной сессии.
    Если session_id отсутствует или сессия не найдена, возвращается ошибка.
    """
    session_id = session_id_context.get()
    if not session_id:
        raise HTTPException(status_code=403, detail="Access denied. Session ID is required.")
    try:
        SessionModel.get_by_session_id(db, session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    files = db.query(File).filter(File.session_id == session_id).all()

    return files


@router.get("/files/original/{file_id}")
def download_original_file(file_id: int, db: Session = Depends(get_db)):
    """
    Скачивание оригинального файла, доступно только для указанной сессии.
    """
    session_id = session_id_context.get()
    return download_file(
        file_id=file_id,
        session_id=session_id,
        file_type=FileTypeInSystemEnum.ORIGINAL,
        db=db
    )

@router.get("/files/pdf/{file_id}")
def download_pdf_file(file_id: int, db: Session = Depends(get_db)):
    """
    Скачивание PDF-файла, доступно только для указанной сессии.
    """
    session_id = session_id_context.get()
    return download_file(
        file_id=file_id,
        session_id=session_id,
        file_type=FileTypeInSystemEnum.CONVERTED,
        db=db
    )
