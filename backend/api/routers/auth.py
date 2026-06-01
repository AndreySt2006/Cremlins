from typing import Optional

from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..schemas import User, AuthResponse
from ..core import security
from ..database import get_db
from ..models import User as DBUser


router = APIRouter(prefix="/api/auth", tags=["auth"])


# Request bodies
class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


@router.post("/login", response_model=AuthResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    db_user = db.query(DBUser).filter(DBUser.email == body.email).first()
    if not db_user or not security.verify_password(body.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    token = security.create_access_token({"user_id": db_user.id, "username": db_user.username})
    public = User(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        avatarUrl=db_user.avatar_url,
        createdAt=(db_user.created_at.isoformat() if db_user.created_at else ""),
    )
    return AuthResponse(user=public, accessToken=token)


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    # check unique email
    if db.query(DBUser).filter(DBUser.email == body.email).first():
        raise HTTPException(status_code=409, detail="Email уже занят")
    hashed = security.get_password_hash(body.password)
    user_obj = DBUser(username=body.username, email=body.email, hashed_password=hashed)
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    token = security.create_access_token({"user_id": user_obj.id, "username": user_obj.username})
    public = User(
        id=user_obj.id,
        username=user_obj.username,
        email=user_obj.email,
        avatarUrl=user_obj.avatar_url,
        createdAt=(user_obj.created_at.isoformat() if user_obj.created_at else ""),
    )
    return AuthResponse(user=public, accessToken=token)


@router.get("/me", response_model=User)
def get_me(authorization: Optional[str] = Header(default=None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Не авторизован")
    token = authorization.split(" ", 1)[1]
    try:
        payload = security.decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Не авторизован")
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return User(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        avatarUrl=db_user.avatar_url,
        createdAt=(db_user.created_at.isoformat() if db_user.created_at else ""),
    )
