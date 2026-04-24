from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.db import Base, SessionLocal, engine
from app.core.settings import get_settings
from app.models import auth  # noqa: F401
from app.services.auth_service import ensure_seed_data

settings = get_settings()


def ensure_database_ready() -> None:
    database_path = settings.resolved_database_path
    if database_path is not None:
        database_path.parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        ensure_seed_data(db)


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_database_ready()
    settings.resolved_upload_dir.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    swagger_ui_parameters={'persistAuthorization': True},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, 'http://localhost:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.mount('/static/uploads', StaticFiles(directory=settings.resolved_upload_dir), name='uploads')
app.include_router(api_router)
