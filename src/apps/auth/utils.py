from datetime import UTC, datetime, timedelta
from typing import Annotated

from aiosqlite import Connection
from fastapi import Depends, HTTPException, status
from fastapi.responses import Response
from fastapi.security import APIKeyCookie
from jwt import ExpiredSignatureError, InvalidSignatureError, decode, encode

from apps.users.password_helper import PasswordHelper
from core.models import UserCreate, UserRead
from core.settings import settings
from database.orm import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_name,
)
from database.utils import get_connection

auth_cookie = APIKeyCookie(name=settings.auth.cookie_key)


async def check_exists_user(username: str, email: str, con: Connection) -> None:
    """Проверка существования пользователя по имени ил почте"""
    if (username and await get_user_by_name(con, username)) or (
        email and await get_user_by_email(con, username)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is already exists",
        )


async def register_user(user_create: UserCreate, con: Connection) -> UserRead:
    """Регистрация нового пользователя"""
    password_helper = PasswordHelper()
    password_helper.check_created_password(user_create)

    user_data = {**user_create.model_dump()}

    user_data.pop("check_password")
    user_data["hashed_password"] = password_helper.hash(user_data.pop("password"))

    await create_user(con, user_data)

    return await get_user_by_name(con, user_create.username)


async def cookie_login(
    access_key: Annotated[str, Depends(auth_cookie)],
    con: Annotated[Connection, Depends(get_connection)],
) -> UserRead:
    """Авторизация пользователя по COOKIE"""
    payload = decode_jwt(access_key)
    user_id = payload.get("sub")

    user = await get_user_by_id(con, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User inactive",
        )

    return user


def set_auth_cookie(
    user: UserRead,
    response: Response,
) -> None:
    """Назначение сессии при помощи JWT и COOKIE"""
    jwt_payload = {
        "sub": user.id,
    }

    access_token = encode_jwt(
        payload=jwt_payload,
        token_age=settings.auth.access_token_age,
    )

    response.set_cookie(key=settings.auth.cookie_key, value=access_token)


def encode_jwt(
    payload: dict,
    private_key: str | None = None,
    algorithm: str | None = None,
    token_age: int | None = None,
) -> str:
    """Создание JWT токена"""
    if private_key is None:
        private_key = settings.auth.private_key.read_text(
            encoding=settings.base_encoding,
        )

    if algorithm is None:
        algorithm = settings.auth.jwt_algorithm

    if token_age is None:
        token_age = settings.auth.access_token_age

    now = datetime.now(UTC)

    to_encode = payload.copy()
    to_encode.update(exp=now + timedelta(seconds=token_age), iat=now)

    return encode(payload=to_encode, key=private_key, algorithm=algorithm)


def decode_jwt(
    jwt: bytes | str,
    public_key: str | None = None,
    algorithm: str | None = None,
) -> dict:
    """Чтение JWT токена"""
    if public_key is None:
        public_key = settings.auth.public_key.read_text(encoding=settings.base_encoding)

    if algorithm is None:
        algorithm = settings.auth.jwt_algorithm

    try:
        payload = decode(jwt=jwt, key=public_key, algorithms=[algorithm])

    except (InvalidSignatureError, ExpiredSignatureError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad signature",
        )

    return payload
