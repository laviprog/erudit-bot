from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.config import settings

DATABASE_ASYNC_URL = (f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}"
                      f":{settings.DB_PORT}/{settings.DB_NAME}")

engine = create_async_engine(DATABASE_ASYNC_URL, future=True, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session
