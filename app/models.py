from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship

from app.enums import FileStatusEnum

from typing import Optional

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    def save(self, db: Session):
        """
        Сохраняет объект в базе данных: добавляет, выполняет коммит и обновляет объект.
        """
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    @classmethod
    def get_by_id(cls, db: Session, object_id: int):
        """Получает объект по ID."""
        instance = db.query(cls).filter_by(id=object_id).first()
        if not instance:
            raise ValueError(f"{cls.__name__} with ID {object_id} not found.")
        return instance


class Session(BaseModel):
    """Класс модель для сессий пользователей"""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    browser = Column(String(255), nullable=True)
    files = relationship("File", back_populates="session")

    @classmethod
    def get_by_session_id(cls, db: Session, session_id: str):
        """Получает сессию по её идентификатору."""
        instance = db.query(cls).filter_by(session_id=session_id).first()
        if not instance:
            raise ValueError(f"Session with ID {session_id} not found.")
        return instance

    def __repr__(self):
        return f"<Session(session_id={self.session_id}, created_at={self.created_at}, browser={self.browser})>"


class File(BaseModel):
    """Класс модель для файлов."""
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("sessions.session_id"), nullable=False)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(255), nullable=False)
    size = Column(Integer)
    extension = Column(String(10))
    status = Column(Enum(FileStatusEnum), default=FileStatusEnum.UPLOADED)
    pdf_path = Column(String(255), nullable=True)
    session = relationship("Session", back_populates="files")

    def update_status(self, db: Session, status: FileStatusEnum, pdf_path: Optional[str] = None):
        """
            Обновить статус файла в базе данных.
            :param db: Сессия базы данных.
            :param status: Новый статус файла.
            :param pdf_path: Путь к PDF-файлу, если есть.
        """
        self.status = status
        if pdf_path:
            self.pdf_path = pdf_path
        self.save(db)

    def __repr__(self):
        return f"<File(filename={self.filename}, status={self.status}, session_id={self.session_id})>"

