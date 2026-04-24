from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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

cors_origins = [] if settings.serve_frontend else [settings.frontend_origin, 'http://localhost:5173']
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.mount('/static/uploads', StaticFiles(directory=settings.resolved_upload_dir), name='uploads')
app.include_router(api_router)

frontend_dist_dir = settings.resolved_frontend_dist_dir
frontend_assets_dir = frontend_dist_dir / 'assets'
frontend_index_file = frontend_dist_dir / 'index.html'

if settings.serve_frontend and frontend_dist_dir.exists() and frontend_index_file.exists():
    if frontend_assets_dir.exists():
        app.mount('/assets', StaticFiles(directory=frontend_assets_dir), name='frontend-assets')

    @app.get('/', include_in_schema=False)
    async def serve_frontend_index() -> FileResponse:
        return FileResponse(frontend_index_file)

    @app.get('/{full_path:path}', include_in_schema=False)
    async def serve_frontend_app(full_path: str) -> FileResponse:
        requested_path = frontend_dist_dir / full_path
        if full_path and requested_path.exists() and requested_path.is_file():
            return FileResponse(requested_path)
        return FileResponse(frontend_index_file)
