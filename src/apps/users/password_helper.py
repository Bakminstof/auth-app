from bcrypt import checkpw, gensalt, hashpw
from fastapi import HTTPException, status

from core.models import UserCreate, UserUpdate
from core.settings import settings


class PasswordHelper:
    def check_created_password(self, user_form: UserCreate | UserUpdate) -> None:
        if user_form.password != user_form.check_password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Passwords don't match",
            )

    def hash(self, password: str) -> bytes:
        return hashpw(
            password=password.encode(encoding=settings.base_encoding),
            salt=gensalt(),
        )

    def validate(self, password: str, hashed_password: bytes) -> bool:
        if not password:
            return False

        return checkpw(
            password=password.encode(encoding=settings.base_encoding),
            hashed_password=hashed_password,
        )
