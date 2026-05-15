from slowapi import Limiter
from fastapi import Request

def get_real_ip(request: Request):
    x_forwarded = request.headers.get("X-Forwarded-For")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.client.host

limiter = Limiter(key_func=get_real_ip)
