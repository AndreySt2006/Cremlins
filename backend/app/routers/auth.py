"""
Роутер: /api/auth

Endpoints: /login, /register, /me

Все endpoint'ы — mock: любые credentials принимаются,
любой Bearer-токен считается валидным.

При реализации реальной логики:
  /login    — проверять хэш пароля bcrypt, возвращать подписанный JWT.
  /register — проверять уникальность email, хэшировать пароль, сохранять в БД.
  /me       — верифицировать JWT (подпись + exp), возвращать реального пользователя.
"""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

from ..schemas import User, AuthResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    """Тело запроса для POST /api/auth/login."""
    email: str
    password: str


class RegisterRequest(BaseModel):
    """Тело запроса для POST /api/auth/register."""
    username: str
    email: str
    password: str


# ---------------------------------------------------------------------------
# Фейковые данные по умолчанию (mock)
# ---------------------------------------------------------------------------

_FAKE_TOKEN = "mock-jwt-token-abc123"

_DEFAULT_USER = User(
    id=42,
    username="test_user",
    email="test@example.com",
    avatarUrl=None,
    createdAt="2024-01-01T00:00:00Z",
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Войти в аккаунт",
    description=(
        "Принимает JSON: { email, password }.\n\n"
        "MOCK: любые credentials → возвращает AuthResponse с фейковым токеном.\n\n"
        "При реализации:\n"
        "  - найти пользователя по email;\n"
        "  - проверить пароль через bcrypt.verify;\n"
        "  - при несовпадении вернуть 401 с сообщением «Неверный email или пароль»;\n"
        "  - сгенерировать JWT (HS256, exp = 7 дней) и вернуть AuthResponse."
    ),
)
def login(body: LoginRequest) -> AuthResponse:
    """Mock-логин: возвращает фейкового пользователя и токен."""
    return AuthResponse(user=_DEFAULT_USER, accessToken=_FAKE_TOKEN)


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=201,
    summary="Зарегистрировать аккаунт",
    description=(
        "Принимает JSON: { username, email, password }.\n\n"
        "MOCK: любые данные → возвращает AuthResponse с переданными username/email.\n\n"
        "При реализации:\n"
        "  - проверить уникальность email (409 если занят);\n"
        "  - хэшировать пароль (bcrypt);\n"
        "  - сохранить нового пользователя в БД;\n"
        "  - сгенерировать JWT и вернуть AuthResponse."
    ),
)
def register(body: RegisterRequest) -> AuthResponse:
    """Mock-регистрация: возвращает нового пользователя из переданных данных."""
    new_user = User(
        id=99,
        username=body.username,
        email=body.email,
        avatarUrl=None,
        createdAt="2024-01-01T00:00:00Z",
    )
    return AuthResponse(user=new_user, accessToken=_FAKE_TOKEN)


@router.get(
    "/me",
    response_model=User,
    summary="Текущий пользователь",
    description=(
        "Возвращает профиль авторизованного пользователя.\n\n"
        "Требует заголовок: Authorization: Bearer <token>.\n"
        "Без токена или с некорректным форматом → 401 Unauthorized.\n\n"
        "MOCK: любой непустой токен → возвращает фейкового пользователя.\n\n"
        "При реализации:\n"
        "  - верифицировать JWT (подпись + срок действия);\n"
        "  - извлечь user_id из payload;\n"
        "  - вернуть пользователя из БД или 401 если токен невалиден."
    ),
)
def get_me(authorization: Optional[str] = Header(default=None)) -> User:
    """Возвращает текущего пользователя по Bearer-токену или 401."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Не авторизован")
    return _DEFAULT_USER
