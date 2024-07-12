from typing import Annotated

from aiosqlite import Connection
from fastapi import Depends, HTTPException, status

from apps.auth.utils import check_exists_user
from apps.users.password_helper import PasswordHelper
from core.models import UserRead, UserUpdate
from database.orm import delete_user, get_user_by_id, get_users_list, update_user
from database.utils import get_connection


async def get_all_users(
    connection: Annotated[Connection, Depends(get_connection)],
) -> list[UserRead]:
    """Получить всех активных пользователей"""
    return await get_users_list(connection)


async def patch_user(
    user_id: int,
    user_update: UserUpdate,
    con: Connection,
) -> UserRead:
    """Обновление данных пользователя по ID"""
    if not await get_user_by_id(con, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user_update.username or user_update.email:
        await check_exists_user(user_update.username, user_update.email, con)

    user_data = {**user_update.model_dump(exclude_unset=True)}

    if user_update.password:
        password_helper = PasswordHelper()
        password_helper.check_created_password(user_update)

        user_data.pop("check_password")
        user_data["hashed_password"] = password_helper.hash(user_data.pop("password"))

    if user_data:
        await update_user(con, user_id, user_data)

    return await get_user_by_id(con, user_id)


async def remove_user(user_id: int, con: Connection, soft: bool = True) -> None:
    """Удаление пользователя по ID"""
    if not await get_user_by_id(con, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await delete_user(con, user_id, soft)
