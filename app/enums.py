import enum

class FileStatusEnum(enum.Enum):
    uploaded = "Загружен"
    processing = "В обработке"
    processed = "done"
    error = "Ошибка конвертации"

class FileExtensionEnum(enum.Enum):
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    BMP = "bmp"
    EPS = "eps"

class FileTypeInSystemEnum(enum.Enum):
    ORIGINAL = "original"
    CONVERTED = "converted"

class CheckMessageEnam(enum.Enum):
    SUCCESSFUL_CHECK = f"✅ Successfully connected to "
    FAILED_CHECK = f"❌ Failed to connect to "
    SUCCESSFUL_CONVERT = f"✅ Successfully converted image to PDF"
    FAILED_CONVERT = f"❌ Error converting file to PDF"