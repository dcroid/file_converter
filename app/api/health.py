from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    """Роут проверки статуса сервиса."""
    return {"status": "Service is running"}
