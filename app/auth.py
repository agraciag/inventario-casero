from passlib.hash import pbkdf2_sha256
from itsdangerous import URLSafeTimedSerializer
from fastapi import Request, HTTPException
from starlette.responses import RedirectResponse

from app.config import SECRET_KEY

serializer = URLSafeTimedSerializer(SECRET_KEY)
COOKIE_NAME = "inventario_session"
MAX_AGE = 60 * 60 * 24 * 90  # 90 days


def hash_pin(pin: str) -> str:
    return pbkdf2_sha256.hash(pin)


def verify_pin(pin: str, hashed: str) -> bool:
    return pbkdf2_sha256.verify(pin, hashed)


def create_session(user_id: int) -> str:
    return serializer.dumps({"user_id": user_id})


def get_session_user_id(request: Request) -> int | None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    try:
        data = serializer.loads(token, max_age=MAX_AGE)
        return data.get("user_id")
    except Exception:
        return None


def set_session_cookie(response: RedirectResponse, user_id: int) -> RedirectResponse:
    token = create_session(user_id)
    response.set_cookie(COOKIE_NAME, token, max_age=MAX_AGE, httponly=True, samesite="lax")
    return response


def clear_session_cookie(response: RedirectResponse) -> RedirectResponse:
    response.delete_cookie(COOKIE_NAME)
    return response


def require_login(request: Request) -> int:
    """Returns user_id or raises redirect to login."""
    user_id = get_session_user_id(request)
    if user_id is None:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    return user_id
