from datetime import datetime, timedelta
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import LoginRequest
from src.config import settings
from src.database import get_db
from src.database.queries import get_admin_by_username

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": int(expire.timestamp()), "token_type": "bearer"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str | None = payload.get("sub")

        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: missing subject")

        return username

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_admin(token: str = Depends(oauth2_scheme)):
    return verify_token(token)


router = APIRouter()


@router.post("/token")
async def login_admin(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    admin = await get_admin_by_username(db, request.username)

    if not admin or not verify_password(request.password, admin.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({"sub": admin.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/verify")
async def verify(current_admin: str = Depends(get_current_admin)):
    return {"message": "ok"}
