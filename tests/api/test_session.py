import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime
from app.main import app
from app.models import Session as SessionModel
from unittest.mock import patch

client = TestClient(app)

@pytest.fixture
def db_mock():
    db = MagicMock()
    yield db
    db.close()

@patch("app.schemas.BASE_URL", "http://testserver")
def test_create_session_success(db_mock):
    """
    Тестирует успешное создание новой сессии.
    """
    # Мок для модели Session
    SessionModel.save = MagicMock(return_value=SessionModel(
        id=1,
        session_id="mock_session_id",
        browser="TestBrowser",
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow(),
    ))

    headers = {"User-Agent": "TestBrowser"}
    response = client.post("/sessions/", headers=headers)

    assert response.status_code == 200
    response_data = response.json()
    assert "session_id" in response_data
    assert "browser" in response_data
    assert response_data["browser"] == "TestBrowser"
