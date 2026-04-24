from typing import Any, Optional


def success(data: Any = None, message: str = "Thanh cong") -> dict:
    return {"success": True, "message": message, "data": data}


def error(message: str, code: int = 400) -> dict:
    return {"success": False, "message": message, "data": None}


def paginate(items: list, total: int, limit: int) -> dict:
    return {"total": total, "limit": limit, "items": items}