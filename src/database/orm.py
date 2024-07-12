from aiosqlite import Connection, Cursor

from core.models import UserRead


async def _get_user(con: Connection, stmt: str, param: str | int) -> UserRead | None:
    async with con.cursor() as cursor:  # type: Cursor
        res = await cursor.execute(stmt, [param])
        res = await res.fetchone()
        await con.commit()

        if not res:
            return

        return UserRead(id=res[0], username=res[1], email=res[2], status=res[3])


async def get_user_by_name(
    con: Connection,
    name: str,
    is_active: bool = True,
) -> UserRead | None:
    stmt = f"""
        SELECT user.id, user.username, user.email, user.status 
        FROM user
        WHERE {"user.status = 'active' AND" if is_active else ""} user.username = ?;
    """
    return await _get_user(con, stmt, name)


async def get_user_by_id(
    con: Connection,
    user_id: int,
    is_active: bool = True,
) -> UserRead | None:
    stmt = f"""
        SELECT user.id, user.username, user.email, user.status 
        FROM user
        WHERE {"user.status = 'active' AND" if is_active else ""} user.id = ?;
    """
    return await _get_user(con, stmt, user_id)


async def get_user_by_email(
    con: Connection,
    email: str,
    is_active: bool = True,
) -> UserRead | None:
    stmt = f"""
        SELECT user.id, user.username, user.email, user.status 
        FROM user
        WHERE {"user.status = 'active' AND" if is_active else ""} user.email = ?;
    """
    return await _get_user(con, stmt, email)


async def get_users_list(
    con: Connection,
    is_active: bool = True,
) -> list[UserRead]:
    stmt = f"""
        SELECT user.id, user.username, user.email, user.status 
        FROM user
        {"WHERE user.status = 'active'" if is_active else ""};
    """
    async with con.cursor() as cursor:  # type: Cursor
        result = await cursor.execute(stmt)
        result = [
            UserRead(id=res[0], username=res[1], email=res[2], status=res[3])
            for res in await result.fetchall()
        ]

        await con.commit()

        return result


async def create_user(con: Connection, user_create_data: dict) -> bool:
    stmt = """
        INSERT INTO user (email, username, status, hashed_password) VALUES (?, ?, ?, ?);
    """

    async with con.cursor() as cursor:  # type: Cursor
        res = await cursor.execute(
            stmt,
            [
                user_create_data.get("email"),
                user_create_data.get("username"),
                user_create_data.get("status"),
                user_create_data.get("hashed_password"),
            ],
        )
        await con.commit()

        return bool(res.rowcount)


async def update_user(con: Connection, user_id: int, user_update_data: dict) -> bool:
    user_update_data_fields = list(user_update_data.keys())

    setter = ", ".join([f"{field} = ?" for field in user_update_data_fields])

    stmt = f"""
        UPDATE user 
        SET {setter}
        WHERE id = ?;
    """

    async with con.cursor() as cursor:  # type: Cursor
        res = await cursor.execute(
            stmt,
            [
                *[user_update_data.get(field) for field in user_update_data_fields],
                user_id,
            ],
        )
        await con.commit()
        return bool(res.rowcount)


async def delete_user(con: Connection, user_id: int, soft: bool = True) -> bool:
    if soft:
        stmt = """
            UPDATE user 
            SET status = 'inactive'
            WHERE id = ?;
        """
    else:
        stmt = """
            DELETE FROM user 
            WHERE id = ?;
        """
    async with con.cursor() as cursor:  # type: Cursor
        result = await cursor.execute(stmt, [user_id])
        await con.commit()
        return bool(result.rowcount)
