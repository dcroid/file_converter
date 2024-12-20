from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.context import session_id_context
from app.enums import FileStatusEnum
from app.config import BASE_URL


class SessionResponse(BaseModel):
    """Схема запроса ответа после создании сессии."""
    id: int
    session_id: str
    created_at: datetime
    last_login: datetime
    browser: str

    class Config:
        from_attributes = True


class FileResponse(BaseModel):
    """Схема ответа после загрузки файла."""
    id: int
    filename: str
    size: int
    extension: str
    status: FileStatusEnum
    pdf_url: Optional[str] = Field(default=None)
    original_url: Optional[str] = Field(default=None)

    class Config:
        from_attributes = True

    @model_validator(mode="after")
    def add_urls(self):
        """
        Генерация ссылок для скачивания файлов.
        """
        session_id = session_id_context.get()
        if session_id:
            self.pdf_url = (
                f"{BASE_URL}/files/pdf/{self.id}?session_id={session_id}"
                if self.status == FileStatusEnum.PROCESSED and self.pdf_url is None
                else None
            )
            self.original_url = f"{BASE_URL}/files/original/{self.id}?session_id={session_id}"
        return self
