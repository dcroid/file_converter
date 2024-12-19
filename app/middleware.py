from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.context import session_id_context


class SessionIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        session_id = request.query_params.get("session_id")
        if session_id:
            session_id_context.set(session_id)
        else:
            session_id_context.set(None)
        return await call_next(request)
