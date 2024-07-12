from typing import Annotated

from aiosqlite import Connection
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from apps.auth.utils import (
    check_exists_user,
    cookie_login,
    register_user,
    set_auth_cookie,
)
from core.models import UserCreate
from core.settings import settings
from database.orm import get_user_by_name
from database.utils import get_connection

router = APIRouter(prefix="/auth")
security = HTTPBasic()


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
async def login(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    con: Annotated[Connection, Depends(get_connection)],
    response: Response,
):
    user = await get_user_by_name(con, credentials.username)

    if user:
        set_auth_cookie(user, response)

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User inactive",
        )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(cookie_login)],
)
async def logout(response: Response):
    response.delete_cookie(key=settings.auth.cookie_key)


@router.post("/register", status_code=status.HTTP_204_NO_CONTENT)
async def register(
    user_create: UserCreate,
    con: Annotated[Connection, Depends(get_connection)],
    response: Response,
):
    await check_exists_user(user_create.username, user_create.email, con)
    new_user = await register_user(user_create, con)
    set_auth_cookie(new_user, response)
