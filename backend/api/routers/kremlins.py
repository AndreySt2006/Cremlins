from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Header, Depends
from typing import Optional

import os
import shutil
import uuid
from sqlalchemy.orm import Session
from ..database import get_db

from ..schemas import KremlinListItem, KremlinDetail, KremlinLocation, Comment
from ..core import security
from ..database import engine
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix="/api/kremlins", tags=["kremlins"])

# ---------------------------------------------------------------------------
# Хардкодные данные (mock)
# ---------------------------------------------------------------------------

KREMLINS_DATA: list[KremlinDetail] = [
    KremlinDetail(
        id=1,
        name="Московский Кремль",
        city="Москва",
        yearBuilt=1485,
        location=KremlinLocation(lat=55.7520, lon=37.6175),
        previewImageUrl="https://placehold.co/400x300?text=Moscow",
        description=(
            "Московский Кремль — древнейшая часть Москвы, главный "
            "общественно-политический и историко-художественный комплекс города. "
            "Современные белокаменные стены были возведены в 1485–1495 годах "
            "итальянскими зодчими по приказу Ивана III."
        ),
        wikipediaUrl="https://ru.wikipedia.org/wiki/Московский_Кремль",
        wikidataId="Q5110",
        images=[
            "https://placehold.co/800x500?text=Moscow+1",
            "https://placehold.co/800x500?text=Moscow+2",
        ],
        commentsCount=3,
    ),
    KremlinDetail(
        id=2,
        name="Нижегородский Кремль",
        city="Нижний Новгород",
        yearBuilt=1515,
        location=KremlinLocation(lat=56.3269, lon=44.0059),
        previewImageUrl="https://placehold.co/400x300?text=Nizhny",
        description=(
            "Нижегородский кремль — каменная крепость в Нижнем Новгороде, "
            "возведённая в 1500–1515 годах. Он сыграл ключевую роль в обороне "
            "Московского государства от казанских ханов."
        ),
        wikipediaUrl="https://ru.wikipedia.org/wiki/Нижегородский_кремль",
        wikidataId="Q1776946",
        images=[
            "https://placehold.co/800x500?text=Nizhny+1",
            "https://placehold.co/800x500?text=Nizhny+2",
        ],
        commentsCount=2,
    ),
    KremlinDetail(
        id=3,
        name="Казанский Кремль",
        city="Казань",
        yearBuilt=1500,
        location=KremlinLocation(lat=55.7986, lon=49.1059),
        previewImageUrl="https://placehold.co/400x300?text=Kazan",
        description=(
            "Казанский Кремль — единственный в мире образец татарского "
            "зодчества, включённый в список Всемирного наследия ЮНЕСКО. "
            "Белокаменные стены были построены псковскими мастерами в XVI веке "
            "после завоевания Казани Иваном Грозным."
        ),
        wikipediaUrl="https://ru.wikipedia.org/wiki/Казанский_кремль",
        wikidataId="Q193171",
        images=["https://placehold.co/800x500?text=Kazan+1"],
        commentsCount=0,
    ),
    KremlinDetail(
        id=4,
        name="Псковский Кром",
        city="Псков",
        yearBuilt=1330,
        location=KremlinLocation(lat=57.8194, lon=28.3324),
        previewImageUrl="https://placehold.co/400x300?text=Pskov",
        description=(
            "Псковский Кром (кремль) — средневековая крепость на мысу "
            "слияния рек Великой и Псковы. Каменные укрепления строились "
            "с XII по XVII век и выдержали около 30 осад."
        ),
        wikipediaUrl="https://ru.wikipedia.org/wiki/Псковский_кром",
        wikidataId="Q2478287",
        images=["https://placehold.co/800x500?text=Pskov+1"],
        commentsCount=0,
    ),
    KremlinDetail(
        id=5,
        name="Новгородский Детинец",
        city="Великий Новгород",
        yearBuilt=1333,
        location=KremlinLocation(lat=58.5219, lon=31.2753),
        previewImageUrl="https://placehold.co/400x300?text=Novgorod",
        description=(
            "Новгородский детинец (кремль) — один из древнейших кремлей России, "
            "впервые упомянутый в летописях в 1044 году. Дошедшие до нас "
            "кирпичные стены были возведены в 1333–1430 годах."
        ),
        wikipediaUrl="https://ru.wikipedia.org/wiki/Новгородский_детинец",
        wikidataId="Q1891120",
        images=["https://placehold.co/800x500?text=Novgorod+1"],
        commentsCount=0,
    ),
    KremlinDetail(
        id=6,
        name="Смоленская крепостная стена",
        city="Смоленск",
        yearBuilt=1602,
        location=KremlinLocation(lat=54.7826, lon=32.0453),
        previewImageUrl="https://placehold.co/400x300?text=Smolensk",
        description=(
            "Смоленская крепость была построена в 1595–1602 годах по приказу "
            "царя Фёдора Иоанновича и Бориса Годунова как щит на западных "
            "рубежах России. Современники называли её «ожерельем всея Руси»."
        ),
        wikipediaUrl="https://ru.wikipedia.org/wiki/Смоленская_крепостная_стена",
        wikidataId="Q4453606",
        images=["https://placehold.co/800x500?text=Smolensk+1"],
        commentsCount=0,
    ),
    KremlinDetail(
        id=7,
        name="Тульский Кремль",
        city="Тула",
        yearBuilt=1520,
        location=KremlinLocation(lat=54.1927, lon=37.6145),
        previewImageUrl="https://placehold.co/400x300?text=Tula",
        description=(
            "Тульский кремль — каменная крепость в центре Тулы, "
            "возведённая в 1507–1520 годах. В 1552 году крепость успешно "
            "выдержала осаду 30-тысячного крымскотатарского войска."
        ),
        wikipediaUrl="https://ru.wikipedia.org/wiki/Тульский_кремль",
        wikidataId="Q1195017",
        images=["https://placehold.co/800x500?text=Tula+1"],
        commentsCount=0,
    ),
    KremlinDetail(
        id=8,
        name="Рязанский Кремль",
        city="Рязань",
        yearBuilt=1095,
        location=KremlinLocation(lat=54.6269, lon=39.7472),
        previewImageUrl="https://placehold.co/400x300?text=Ryazan",
        description=(
            "Рязанский кремль — историческое ядро города, расположенное "
            "на высоком холме у слияния рек Трубеж и Лыбедь. "
            "Музей-заповедник хранит архитектурные памятники XI–XIX веков."
        ),
        wikipediaUrl="https://ru.wikipedia.org/wiki/Рязанский_кремль",
        wikidataId="Q2331017",
        images=["https://placehold.co/800x500?text=Ryazan+1"],
        commentsCount=0,
    ),
    KremlinDetail(
        id=9,
        name="Коломенский Кремль",
        city="Коломна",
        yearBuilt=1531,
        location=KremlinLocation(lat=55.0966, lon=38.7728),
        previewImageUrl="https://placehold.co/400x300?text=Kolomna",
        description=(
            "Коломенский кремль — одна из крупнейших крепостей средневековой "
            "Руси, строительство которой завершилось в 1531 году. "
            "Крепость защищала Москву с юго-востока от набегов крымских татар."
        ),
        wikipediaUrl="https://ru.wikipedia.org/wiki/Коломенский_кремль",
        wikidataId="Q2363450",
        images=["https://placehold.co/800x500?text=Kolomna+1"],
        commentsCount=0,
    ),
    KremlinDetail(
        id=10,
        name="Зарайский Кремль",
        city="Зарайск",
        yearBuilt=1531,
        location=KremlinLocation(lat=54.7644, lon=38.8815),
        previewImageUrl="https://placehold.co/400x300?text=Zaraisk",
        description=(
            "Зарайский кремль — самый маленький из сохранившихся кремлей России, "
            "построенный в 1528–1531 годах по приказу Василия III. "
            "Прямоугольная крепость с семью башнями хорошо сохранилась до наших дней."
        ),
        wikipediaUrl="https://ru.wikipedia.org/wiki/Зарайский_кремль",
        wikidataId="Q4154917",
        images=["https://placehold.co/800x500?text=Zaraisk+1"],
        commentsCount=0,
    ),
]

# Индекс для быстрого поиска по id
_KREMLINS_BY_ID: dict[int, KremlinDetail] = {k.id: k for k in KREMLINS_DATA}

# Хардкодные комментарии (только для первых двух кремлей)
COMMENTS_DATA: dict[int, list[Comment]] = {
    1: [
        Comment(
            id=1, kremlinId=1, authorId=1, authorName="Алексей Иванов",
            text="Был здесь летом — грандиозное место! Башни выглядят монументально.",
            imageUrls=[], createdAt="2024-07-15T10:30:00Z",
        ),
        Comment(
            id=2, kremlinId=1, authorId=2, authorName="Мария Смирнова",
            text="Обязательно к посещению. Советую приходить рано утром, пока нет толп.",
            imageUrls=["https://placehold.co/400x300?text=photo"],
            createdAt="2024-08-01T08:00:00Z",
        ),
        Comment(
            id=3, kremlinId=1, authorId=3, authorName="Дмитрий Козлов",
            text="Оружейная палата — отдельный восторг, не пропустите.",
            imageUrls=[], createdAt="2024-09-10T14:20:00Z",
        ),
    ],
    2: [
        Comment(
            id=4, kremlinId=2, authorId=1, authorName="Алексей Иванов",
            text="Красивый вид с Часовой башни на Волгу и Оку.",
            imageUrls=[], createdAt="2024-06-20T16:00:00Z",
        ),
        Comment(
            id=5, kremlinId=2, authorId=4, authorName="Ольга Петрова",
            text="Очень атмосферный кремль. Жаль, что туристов мало — недооценённое место.",
            imageUrls=[], createdAt="2024-06-25T11:45:00Z",
        ),
    ],
}

# Счётчик id для новых комментариев (в реальной реализации — из БД)
_next_comment_id = 100


# ---------------------------------------------------------------------------
# Вспомогательная функция проверки авторизации (заглушка)
# ---------------------------------------------------------------------------

def _require_auth(authorization: Optional[str]) -> dict:
    """
    Проверяет Bearer-токен и возвращает payload токена (например user_id, username).
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Не авторизован")
    token = authorization.split(" ", 1)[1]
    try:
        payload = security.decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Не авторизован")
    return payload


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=list[KremlinListItem],
    summary="Список всех кремлей",
    description=(
        "Возвращает краткую карточку каждого кремля: id, название, координаты, "
        "превью-изображение, город, год постройки. "
        "Используется для отображения маркеров на карте и в общем списке. "
        "Не содержит description и полного списка фото — за ними идти на /api/kremlins/{id}."
    ),
)
def list_kremlins() -> list[KremlinListItem]:
    """Возвращает все кремли как KremlinListItem (без тяжёлых полей).

    Пытаемся прочитать из БД (таблица fortresses). Если подключение к БД
    не удалось — возвращаем mock-данные из KREMLINS_DATA.
    """
    try:
        with engine.connect() as conn:
            q = text(
                "SELECT id, name, ST_X(location) AS lon, ST_Y(location) AS lat, image_url, foundation_year, city FROM fortresses")
            res = conn.execute(q)
            items: list[KremlinListItem] = []
            for row in res.mappings():
                lat = row.get("lat")
                lon = row.get("lon")
                if lat is None or lon is None:
                    continue
                loc = KremlinLocation(lat=lat, lon=lon)
                items.append(KremlinListItem(
                    id=row["id"],
                    name=row["name"],
                    location=loc,
                    previewImageUrl=row.get("image_url"),
                    city=row.get("city"),
                    yearBuilt=row.get("foundation_year")
                ))
            if items:
                return items
    except SQLAlchemyError:
        # БД недоступна или запрос не удался — используем mock
        pass

    return [KremlinListItem(**k.model_dump()) for k in KREMLINS_DATA]


@router.get(
    "/{kremlin_id}",
    response_model=KremlinDetail,
    summary="Детальная страница кремля",
    description=(
        "Возвращает полные данные кремля: всё из KremlinListItem плюс "
        "description, wikipediaUrl, wikidataId, images, commentsCount. "
        "Используется на странице /kremlins/{id}. "
        "Возвращает 404, если кремль с таким id не существует."
    ),
)
def get_kremlin(kremlin_id: int) -> KremlinDetail:
    """Возвращает KremlinDetail по id или 404.

    Пытаемся сначала прочитать из БД, иначе возвращаем mock.
    """
    try:
        with engine.connect() as conn:
            q = text(
                "SELECT id, name, ST_X(location) AS lon, ST_Y(location) AS lat, image_url, description, foundation_year, wikipedia_url, wikidata_id FROM fortresses WHERE id = :id"
            )
            res = conn.execute(q, {"id": kremlin_id}).mappings().first()
            if res:
                lat = res.get("lat")
                lon = res.get("lon")
                loc = KremlinLocation(lat=lat or 0.0, lon=lon or 0.0)
                return KremlinDetail(
                    id=res["id"], name=res["name"], location=loc,
                    previewImageUrl=res.get("image_url"), city=None, yearBuilt=res.get("foundation_year"),
                    description=res.get("description"), wikipediaUrl=res.get("wikipedia_url"), wikidataId=res.get("wikidata_id"),
                    images=[res.get("image_url")] if res.get("image_url") else [], commentsCount=0,
                )
    except SQLAlchemyError:
        pass

    kremlin = _KREMLINS_BY_ID.get(kremlin_id)
    if not kremlin:
        raise HTTPException(status_code=404, detail="Кремль не найден")
    return kremlin


@router.get(
    "/{kremlin_id}/comments",
    response_model=list[Comment],
    summary="Комментарии к кремлю",
    description=(
        "Возвращает список комментариев для указанного кремля. "
        "Если кремль не существует — 404. "
        "Пустой массив — нормальный ответ (комментариев ещё нет). "
        "Комментарии отсортированы по убыванию даты (новые первыми). "
        "Пагинация: при реализации добавить query-параметры offset и limit."
    ),
)
def list_comments(kremlin_id: int) -> list[Comment]:
    """Возвращает комментарии к кремлю или 404 если кремль не найден.
    Пытаемся прочитать комментарии из БД, в противном случае — из памяти.
    """
    # Попробуем получить из БД
    try:
        from ..models import Comment as DBComment
        from ..database import SessionLocal
        db = SessionLocal()
        rows = db.query(DBComment).filter(DBComment.kremlin_id == kremlin_id).order_by(DBComment.created_at.desc()).all()
        db.close()
        if rows:
            return [
                Comment(
                    id=r.id,
                    kremlinId=r.kremlin_id,
                    authorId=r.author_id,
                    authorName=r.author_name,
                    authorAvatarUrl=r.author_avatar_url,
                    text=r.text,
                    imageUrls=r.image_urls or [],
                    createdAt=(r.created_at.isoformat() if r.created_at else ""),
                )
                for r in rows
            ]
    except Exception:
        pass

    if kremlin_id not in _KREMLINS_BY_ID:
        raise HTTPException(status_code=404, detail="Кремль не найден")
    return COMMENTS_DATA.get(kremlin_id, [])


@router.post(
    "/{kremlin_id}/comments",
    response_model=Comment,
    status_code=201,
    summary="Добавить комментарий к кремлю",
    description=(
        "Принимает multipart/form-data:\n"
        "  - text (str, обязательно) — текст комментария;\n"
        "  - images (list[UploadFile], опционально) — фотографии.\n\n"
        "Требует авторизации: заголовок Authorization: Bearer <token>. "
        "Без токена — 401 Unauthorized.\n\n"
        "Возвращает созданный Comment с id, kremlinId, временем создания.\n\n"
        "При реализации:\n"
        "  - верифицировать JWT и извлечь authorId;\n"
        "  - сохранить изображения в хранилище, вернуть их URL в imageUrls;\n"
        "  - атомарно инкрементировать commentsCount у кремля;\n"
        "  - сохранить комментарий в БД."
    ),
)
async def create_comment(
    kremlin_id: int,
    text: str = Form(..., description="Текст комментария"),
    images: list[UploadFile] = File(default=[], description="Фотографии (опционально)"),
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> Comment:
    """Создаёт комментарий. Требует Bearer-токен."""
    global _next_comment_id

    user = _require_auth(authorization)

    if kremlin_id not in _KREMLINS_BY_ID and db is None:
        raise HTTPException(status_code=404, detail="Кремль не найден")

    upload_dir = os.path.join("static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    urls: list[str] = []
    for up in images:
        if not up.filename:
            continue
        ext = os.path.splitext(up.filename)[1]
        filename = f"{int(datetime.now().timestamp())}_{uuid.uuid4().hex}{ext}"
        dest_path = os.path.join(upload_dir, filename)
        with open(dest_path, "wb") as f:
            shutil.copyfileobj(up.file, f)
        urls.append(f"/static/uploads/{filename}")

    created_at = datetime.now(timezone.utc)

    try:
        from ..models import Comment as DBComment, Kremlin as DBKremlin

        db_comment = DBComment(
            kremlin_id=kremlin_id,
            author_id=user.get("user_id") or 0,
            author_name=user.get("username") or "Пользователь",
            author_avatar_url=None,
            text=text,
            image_urls=urls,
            created_at=created_at,
        )
        db.add(db_comment)
        kremlin_row = db.query(DBKremlin).filter(DBKremlin.id == kremlin_id).first()
        if kremlin_row:
            kremlin_row.comments_count = (kremlin_row.comments_count or 0) + 1
        db.commit()
        db.refresh(db_comment)

        return Comment(
            id=db_comment.id,
            kremlinId=db_comment.kremlin_id,
            authorId=db_comment.author_id,
            authorName=db_comment.author_name,
            authorAvatarUrl=db_comment.author_avatar_url,
            text=db_comment.text,
            imageUrls=db_comment.image_urls or [],
            createdAt=db_comment.created_at.isoformat(),
        )
    except Exception:
        # если что-то пошло не так с БД — падаем обратно к in-memory
        pass

    # Fallback: store in memory
    comment_id = _next_comment_id
    _next_comment_id += 1

    author_id = user.get("user_id") if isinstance(user, dict) else None
    author_name = user.get("username") if isinstance(user, dict) else "Пользователь"
    new_comment = Comment(
        id=comment_id,
        kremlinId=kremlin_id,
        authorId=author_id or 0,
        authorName=author_name,
        authorAvatarUrl=None,
        text=text,
        imageUrls=urls,  # локальные URL /static/uploads/...
        createdAt=created_at.isoformat(),
    )
    COMMENTS_DATA.setdefault(kremlin_id, []).append(new_comment)
    return new_comment
