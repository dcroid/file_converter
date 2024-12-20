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

class LogMessageEnum(enum.Enum):
    SUCCESSFUL_CHECK = "✅ Successfully connected to {}"
    FAILED_CHECK = "❌ Failed to connect to {}: {}"
    SUCCESSFUL_CONVERT = "✅ Successfully converted {} to PDF: {}"
    FAILED_CONVERT = "❌ Error converting file to PDF {}"
    NOT_FOUND = "⚠️ File not found"
    ACCESS_DENIED = "⛔ Access denied to {}"
    FILE_INVALID_TYPE = "🚫 Invalid file type"
    UNSUPPORTED_FORMAT = "📛 Unsupported file format for conversion"
    DIRECTORIES_ENSURED = "✅ 📂 Directories ensured: '{}' and '{}'"
    FILE_NOT_EXIST = "❓ File '{}' does not exist"
    FILE_TOO_LARGE = "📏❌ File too large (max {} MB)"
    INVALID_SESSION = "🔑❌ Invalid session ID"
