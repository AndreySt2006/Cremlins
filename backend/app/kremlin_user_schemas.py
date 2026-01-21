from pydantic import BaseModel
from typing import Optional, Any

# Базовая схема для Кремля
class KremlinBase(BaseModel):
    name: str
    description: Optional[str] = None
    foundation_year: Optional[int] = None
    architectural_style: Optional[str] = None

class KremlinCreate(KremlinBase):
    pass

class KremlinResponse(KremlinBase):
    id: int
    # Для простоты пока вернем геометрию как строку (WKT) или обработаем позже
    # В идеале здесь стоит использовать geojson pydantic модели
    
    class Config:
        from_attributes = True # В старых версиях Pydantic это было orm_mode = True

# Схемы для пользователя
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
