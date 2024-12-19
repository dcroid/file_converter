import os
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.models import File, Session as SessionModel
from app.enums import FileTypeInSystemEnum
from app.utils.file_handler import download_file


def test_download_original_file():
    """Test downloading the original file."""
    db_mock = MagicMock(spec=Session)

    session_mock = MagicMock()
    session_mock.session_id = "test_session_id"
    SessionModel.get_by_session_id = MagicMock(return_value=session_mock)

    file_mock = MagicMock()
    file_mock.session_id = "test_session_id"
    file_mock.filepath = "/path/to/original/file.txt"
    file_mock.filename = "file.txt"
    File.get_by_id = MagicMock(return_value=file_mock)

    with patch("os.path.exists", return_value=True):
        response = download_file(1, "test_session_id", FileTypeInSystemEnum.ORIGINAL, db_mock)

    assert isinstance(response, FileResponse)
    assert response.path == file_mock.filepath
    assert response.filename == file_mock.filename


def test_download_converted_file():
    """Test downloading the converted PDF file."""
    db_mock = MagicMock(spec=Session)

    session_mock = MagicMock()
    session_mock.session_id = "test_session_id"
    SessionModel.get_by_session_id = MagicMock(return_value=session_mock)

    file_mock = MagicMock()
    file_mock.session_id = "test_session_id"
    file_mock.pdf_path = "/path/to/converted/file.pdf"
    File.get_by_id = MagicMock(return_value=file_mock)

    with patch("os.path.exists", return_value=True):
        response = download_file(1, "test_session_id", FileTypeInSystemEnum.CONVERTED, db_mock)

    assert isinstance(response, FileResponse)
    assert response.path == file_mock.pdf_path
    assert response.filename == os.path.basename(file_mock.pdf_path)


def test_file_not_found():
    """Test when the file does not exist."""
    db_mock = MagicMock(spec=Session)

    session_mock = MagicMock()
    session_mock.session_id = "test_session_id"
    SessionModel.get_by_session_id = MagicMock(return_value=session_mock)

    file_mock = MagicMock()
    file_mock.session_id = "test_session_id"
    file_mock.filepath = None
    File.get_by_id = MagicMock(return_value=file_mock)

    with pytest.raises(HTTPException) as exc_info:
        download_file(1, "test_session_id", FileTypeInSystemEnum.ORIGINAL, db_mock)

    assert exc_info.value.status_code == 404
    assert "File not found." in str(exc_info.value.detail)


def test_access_denied():
    """Test access denied to the file."""
    db_mock = MagicMock(spec=Session)

    session_mock = MagicMock()
    session_mock.session_id = "valid_session_id"
    SessionModel.get_by_session_id = MagicMock(return_value=session_mock)

    file_mock = MagicMock()
    file_mock.session_id = "invalid_session_id"
    File.get_by_id = MagicMock(return_value=file_mock)

    with pytest.raises(HTTPException) as exc_info:
        download_file(1, "valid_session_id", FileTypeInSystemEnum.ORIGINAL, db_mock)

    assert exc_info.value.status_code == 403
    assert "Access denied to this file." in str(exc_info.value.detail)


def test_invalid_file_type():
    """Test invalid file type."""
    db_mock = MagicMock(spec=Session)

    with pytest.raises(ValueError) as exc_info:
        download_file(1, "session_id", FileTypeInSystemEnum("invalid_type"), db_mock)

    assert "invalid_type" in str(exc_info.value)
