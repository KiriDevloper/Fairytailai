from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check():
    """Kiem tra server dang chay."""
    return {
        "status":    "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service":   "Fairytale AI"
    }