from typing import Annotated

from aiosqlite import Connection
from fastapi import APIRouter, Depends, status

from apps.auth.utils import check_exists_user, cookie_login, register_user
from apps.users.utils import get_all_users, patch_user, remove_user
from core.models import UserCreate, UserRead, UserUpdate
from database.utils import get_connection

router = APIRouter(prefix="/users")


@router.get(
    "/all",
    dependencies=[Depends(cookie_login)],
    response_model=list[UserRead],
)
async def users_list(
    users: Annotated[list[UserRead], Depends(get_all_users)],
):
    return users


@router.post(
    "/add",
    dependencies=[Depends(cookie_login)],
    response_model=UserRead,
)
async def users_add(
    user_create: UserCreate,
    con: Annotated[Connection, Depends(get_connection)],
):
    await check_exists_user(user_create.username, user_create.email, con)
    return await register_user(user_create, con)


@router.patch(
    "/{user_id}/update",
    dependencies=[Depends(cookie_login)],
    response_model=UserRead,
)
async def users_update(
    user_id: int,
    user_update: UserUpdate,
    con: Annotated[Connection, Depends(get_connection)],
):
    return await patch_user(user_id, user_update, con)


@router.delete(
    "/{user_id}/delete",
    dependencies=[Depends(cookie_login)],
    status_code=status.HTTP_200_OK,
)
async def users_delete(
    user_id: int,
    con: Annotated[Connection, Depends(get_connection)],
):
    return await remove_user(user_id, con)
