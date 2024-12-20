import os

from fastapi import HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.enums import FileTypeInSystemEnum, LogMessageEnum, HTTPStatusCodeEnum
from app.models import File, Session as SessionModel


def download_file(file_id: int, session_id: str, file_type: FileTypeInSystemEnum, db: Session) -> FileResponse:
    """
    Универсальная функция для скачивания файлов.
    :param file_id: ID файла
    :param session_id: ID сессии
    :param file_type: Тип файла ("original" или "pdf")
    :param db: Сессия базы данных
    :return: FileResponse для скачивания
    """

    session = SessionModel.get_by_session_id(db, session_id)

    file = File.get_by_id(db, file_id)
    if not file or file.session_id != session.session_id:
        raise HTTPException(
            status_code=HTTPStatusCodeEnum.FORBIDDEN.value,
            detail=LogMessageEnum.ACCESS_DENIED.value.format("file")
        )

    if file_type == FileTypeInSystemEnum.ORIGINAL:
        file_path = file.filepath
        filename = file.filename
    elif file_type == FileTypeInSystemEnum.CONVERTED:
        file_path = file.pdf_path
        filename = os.path.basename(file.pdf_path) if file.pdf_path else None
    else:
        raise ValueError(LogMessageEnum.FILE_INVALID_TYPE.value)

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(
            status_code=HTTPStatusCodeEnum.NOT_FOUND.value,
            detail=LogMessageEnum.NOT_FOUND.value)

    return FileResponse(
        path=file_path,
        media_type="application/octet-stream" if file_type == FileTypeInSystemEnum.ORIGINAL.value else "application/pdf",
        filename=filename
    )