
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers import kremlins, auth

app = FastAPI(
    title="Кремли России API",
    description=(
        "REST API для исторического справочника кремлей России.\n\n"
        "**Текущее состояние:** mock-endpoints с хардкодными данными.\n"
        "Все сигнатуры и схемы финализированы — при подключении БД "
        "менять только реализацию внутри роутеров."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Роутеры
# ---------------------------------------------------------------------------

app.include_router(kremlins.router)
app.include_router(auth.router)

# Статические файлы (загруженные изображения)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
def root():
    return {"message": "Кремли России API. Документация: /docs"}
