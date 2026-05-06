"""
🔐 Dependencies - Xác thực & Bảo mật API

Quản lý API Key authentication qua Header X-API-Key.
"""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from config import API_KEY

# ── API Key Header ──────────────────────────────────────────
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    api_key: str = Security(api_key_header),
) -> str:
    """Xác thực API Key từ header request.

    Raises:
        HTTPException 403: Nếu API key không hợp lệ hoặc thiếu.
    """
    if not api_key or api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key không hợp lệ hoặc thiếu. "
                   "Vui lòng thêm header 'X-API-Key'.",
        )
    return api_key
