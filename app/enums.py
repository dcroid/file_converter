import enum

class FileStatusEnum(enum.Enum):
    UPLOADED = "Uploaded"
    PROCESSING = "Processing"
    PROCESSED = "Done"
    ERROR = "Conversion Error"

class FileExtensionEnum(enum.Enum):
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    BMP = "bmp"
    EPS = "eps"

class FileTypeInSystemEnum(enum.Enum):
    ORIGINAL = "original"
    CONVERTED = "converted"

class HTTPStatusCodeEnum(enum.Enum):
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
    BAD_REQUEST = 400
    UNAUTHORIZED = 401

class LogMessageEnum(enum.Enum):
    SUCCESSFUL_CHECK = "✅ Successfully connected to {}"
    FAILED_CHECK = "❌ Failed to connect to {}: {}"
    SUCCESSFUL_CONVERT = "✅ Successfully converted {} to PDF: {}"
    FAILED_CONVERT = "❌ Error converting file to PDF: {}"
    NOT_FOUND = "⚠️ File not found: {}"
    ACCESS_DENIED = "⛔ Access denied to {}"
    FILE_INVALID_TYPE = "🚫 Invalid file type"
    UNSUPPORTED_FORMAT = "📛 Unsupported file format for conversion"
    DIRECTORIES_ENSURED = "📂✅ Directories ensured: '{}' and '{}'"
    FILE_NOT_EXIST = "❓ File '{}' does not exist"
    FILE_TOO_LARGE = "📏❌ File too large (max {} MB)"
    SENTRY_INITIALIZED = "✅ Sentry initialized"
    SENTRY_DSN_NOT_PROVIDED = "⚠️ Sentry DSN not provided. Sentry is disabled."
    SERVICE_STARTUP_ABORTED = "🚫 Service startup aborted. Check database and Redis connections."
    ALL_DEPENDENCIES_AVAILABLE = "✅ All dependencies are available. Service starting..."
    REQUEST = "➡️ Request: {request_method} {request_url}"
    RESPONSE = "⬅️ Response: {response_status_code}"
