from aiosqlite import Connection, Cursor


async def create_table_user(con: Connection) -> None:
    stmt = """
        CREATE TABLE IF NOT EXISTS user (
        id              INTEGER        NOT NULL,
        username        VARCHAR (100)  NOT NULL,
        email           VARCHAR (200)  NOT NULL,
        hashed_password VARCHAR (1000) NOT NULL,
        status          VARCHAR (10)   NOT NULL,

        CONSTRAINT pk_user PRIMARY KEY (
            id
        ),
        CONSTRAINT user__email_uc UNIQUE (
            email
        ),
        CONSTRAINT user__username_uc UNIQUE (   
            username
        )
        );
    """
    async with con.cursor() as cursor:  # type: Cursor
        await cursor.execute(stmt)
