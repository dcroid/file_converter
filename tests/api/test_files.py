import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from app.context import session_id_context
from app.models import Session as SessionModel, File
from app.database import get_db

client = TestClient(app)


# Mock database dependency
def mock_get_db():
    db = MagicMock()
    return db


# Override the dependency in the app
app.dependency_overrides[get_db] = mock_get_db


@pytest.fixture
def mock_db():
    return mock_get_db()


# Test for upload_file
@patch("app.api.files.upload_file.convert_to_pdf_task.delay")
def test_upload_file(mock_convert_to_pdf_task, mock_db):
    session_id_context.set("test_session_id")
    mock_db.query(SessionModel).filter().first.return_value = MagicMock(session_id="test_session_id")
    mock_db.query(File).filter().first.return_value = None

    # Simulate file upload
    file_content = b"Test content"
    response = client.post(
        "/upload/",
        files={"file": ("test.txt", file_content, "text/plain")},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "uploaded"
    mock_convert_to_pdf_task.assert_called_once()


# Test for get_files
def test_get_files(mock_db):
    session_id_context.set("test_session_id")
    mock_db.query(SessionModel).filter().first.return_value = MagicMock(session_id="test_session_id")
    mock_db.query(File).filter().all.return_value = [
        MagicMock(id=1, filename="example.txt", filepath="/path/to/example.txt"),
    ]

    response = client.get("/files/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == 1


# Test for download_original_file
@patch("app.utils.file_handler.download_file")
def test_download_original_file(mock_download_file, mock_db):
    session_id_context.set("test_session_id")
    mock_download_file.return_value = b"File content"

    response = client.get("/files/original/1")

    assert response.status_code == 200
    assert response.content == b"File content"
    mock_download_file.assert_called_once_with(
        file_id=1,
        session_id="test_session_id",
        file_type="original",
        db=mock_db,
    )


# Test for download_pdf_file
@patch("app.utils.file_handler.download_file")
def test_download_pdf_file(mock_download_file, mock_db):
    session_id_context.set("test_session_id")
    mock_download_file.return_value = b"PDF content"

    response = client.get("/files/pdf/1")

    assert response.status_code == 200
    assert response.content == b"PDF content"
    mock_download_file.assert_called_once_with(
        file_id=1,
        session_id="test_session_id",
        file_type="converted",
        db=mock_db,
    )