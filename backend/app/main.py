from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
<<<<<<< HEAD
from app.core.exceptions import install_exception_handlers 
=======
from app.core.exceptions import install_exception_handlers
>>>>>>> 1b8878ef404f483e7609ab1c87da6c2e8c648546
from app.routers import auth, health, platform

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", openapi_url=f"{settings.api_v1_prefix}/openapi.json", docs_url="/docs", redoc_url="/redoc", lifespan=lifespan)
settings.upload_dir.mkdir(parents=True, exist_ok=True)
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_url], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
install_exception_handlers(app)
app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(platform.router, prefix=settings.api_v1_prefix)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
