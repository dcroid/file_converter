from unittest.mock import patch, MagicMock
from app.utils.systems import (
    validate_file_extension,
    convert_to_pdf,
    create_directories,
    get_absolute_path,
)


def test_validate_file_extension():
    assert validate_file_extension(".png") is True
    assert validate_file_extension(".jpg") is True
    assert validate_file_extension(".unsupported") is False


@patch("app.utils.Image.open")
@patch("app.utils.canvas.Canvas")
def test_convert_to_pdf(mock_canvas, mock_image_open):
    # Mock для изображений
    mock_image = MagicMock()
    mock_image.convert.return_value.save.return_value = None
    mock_image_open.return_value = mock_image

    # Проверка конвертации изображений
    convert_to_pdf("test.png", "output.pdf")
    mock_image.convert.assert_called_with("RGB")
    mock_image.convert.return_value.save.assert_called_with("output.pdf", "PDF")

    # Проверка конвертации EPS
    mock_canvas_instance = MagicMock()
    mock_canvas.return_value = mock_canvas_instance
    convert_to_pdf("test.eps", "output.pdf")
    mock_canvas_instance.drawImage.assert_called_with(
        get_absolute_path("test.eps"), 0, 0
    )
    mock_canvas_instance.save.assert_called()


@patch("os.makedirs")
def test_create_directories(mock_makedirs):
    create_directories()
    mock_makedirs.assert_any_call("upload_folder", exist_ok=True)
    mock_makedirs.assert_any_call("pdf_folder", exist_ok=True)
