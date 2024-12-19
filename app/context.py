from contextvars import ContextVar

# Контекстная переменная для session_id
session_id_context: ContextVar[str] = ContextVar("session_id", default=None)