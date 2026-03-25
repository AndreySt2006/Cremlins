"""
Pydantic-схемы — контракт API с фронтендом.

для реализации:
  Схемы финализированы. При переходе от моков к реальной БД
  меняй только данные внутри роутеров — сигнатуры и поля трогать нельзя,
  иначе фронтенд сломается.

  Соглашение по именованию: camelCase (совпадает с frontend/src/types/).
"""

from pydantic import BaseModel
from typing import Optional


# ---------------------------------------------------------------------------
# Kremlin
# ---------------------------------------------------------------------------

class KremlinLocation(BaseModel):
    """Географические координаты в системе WGS-84."""
    lat: float
    lon: float


class KremlinListItem(BaseModel):
    """
    Краткая карточка кремля — используется в списке и на карте.
    Минимум полей, чтобы не перегружать ответ при загрузке всех объектов.
    """
    id: int
    name: str
    location: KremlinLocation
    previewImageUrl: Optional[str] = None
    city: Optional[str] = None
    yearBuilt: Optional[int] = None


class KremlinDetail(KremlinListItem):
    """
    Полная страница кремля. Наследует KremlinListItem.

    Поля:
      description   — 2–3 предложения истории объекта.
      wikipediaUrl  — ссылка на статью Википедии (может отсутствовать).
      wikidataId    — идентификатор Wikidata (например «Q5110»).
      images        — упорядоченный список URL фото; первое — главное.
      commentsCount — кешированный счётчик комментариев;
                      инкрементировать атомарно при POST /comments.
    """
    description: Optional[str] = None
    wikipediaUrl: Optional[str] = None
    wikidataId: Optional[str] = None
    images: list[str] = []
    commentsCount: int = 0


# ---------------------------------------------------------------------------
# Comment
# ---------------------------------------------------------------------------

class Comment(BaseModel):
    """
    Комментарий пользователя к кремлю.

    createdAt  — ISO-8601 строка (например «2024-06-01T12:00:00Z»).
    imageUrls  — публичные URL загруженных фото (пустой список если нет).

    При реализации POST /comments:
      - сохранять файлы в S3 / локальное хранилище;
      - заполнять imageUrls публичными URL;
      - инкрементировать commentsCount у кремля атомарно.
    """
    id: int
    kremlinId: int
    authorId: int
    authorName: str
    authorAvatarUrl: Optional[str] = None
    text: str
    imageUrls: list[str] = []
    createdAt: str


# ---------------------------------------------------------------------------
# Auth / User
# ---------------------------------------------------------------------------

class User(BaseModel):
    """
    Публичный профиль пользователя.
    Никогда не включай hashed_password и другие чувствительные поля.
    createdAt — ISO-8601 строка.
    """
    id: int
    username: str
    email: str
    avatarUrl: Optional[str] = None
    createdAt: str


class AuthResponse(BaseModel):
    """
    Ответ на успешные /auth/login и /auth/register.

    accessToken — Bearer-токен (JWT в реальной реализации).
    Фронтенд сохраняет его в localStorage и отправляет в каждом
    авторизованном запросе: Authorization: Bearer <token>.
    """
    user: User
    accessToken: str
