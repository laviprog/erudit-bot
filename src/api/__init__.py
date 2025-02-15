from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from uvicorn import Config, Server

from src.api.routes.auth import router as auth_router, hash_password
from src.api.routes.users import router as users_router
from src.config import settings
from src.database import async_session
from src.database.models import Admin
from src.database.queries import get_admin_by_username, create_object


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_session() as db:
        admin = await get_admin_by_username(db, settings.ADMIN_USERNAME)

        if not admin:
            await create_object(
                db,
                Admin,
                username=settings.ADMIN_USERNAME,
                password=hash_password(settings.ADMIN_PASSWORD)
            )
    yield


app = FastAPI(
    title="bot-api",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])


async def start_api():
    config = Config(app, host=settings.API_HOST, port=settings.API_PORT, loop="asyncio")
    server = Server(config)
    await server.serve()
