
from pydantic import BaseModel, ConfigDict
from typing import Optional


# ---------------------------------------------------------------------------
# Kremlin
# ---------------------------------------------------------------------------

class BaseSchema(BaseModel):
    """Базовый Pydantic-класс для схем — включает настройку для работы с ORM-объектами.

    Используем ConfigDict(from_attributes=True), чтобы можно было валидировать SQLAlchemy
    объекты через model_validate(obj, from_attributes=True) при необходимости.
    """
    model_config = ConfigDict(from_attributes=True)


class KremlinLocation(BaseSchema):
    """Географические координаты в системе WGS-84."""
    lat: float
    lon: float


class KremlinListItem(BaseSchema):
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
    description: Optional[str] = None
    wikipediaUrl: Optional[str] = None
    wikidataId: Optional[str] = None
    images: list[str] = []
    commentsCount: int = 0


# ---------------------------------------------------------------------------
# Comment
# ---------------------------------------------------------------------------

class Comment(BaseSchema):

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

class User(BaseSchema):
    id: int
    username: str
    email: str
    avatarUrl: Optional[str] = None
    createdAt: str


class AuthResponse(BaseSchema):
    user: User
    accessToken: str
