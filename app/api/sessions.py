import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db

from app.models import Session as SessionModel
from app.schemas import SessionResponse

router = APIRouter()

@router.post("/sessions/", response_model=SessionResponse)
def create_session(request: Request, db: Session = Depends(get_db)):
    browser = request.headers.get("User-Agent", "unknown")
    session_id = str(uuid.uuid4())

    user_session = SessionModel(
        session_id=session_id,
        browser=browser,
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow()
    ).save(db)

    return user_session
