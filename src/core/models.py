from enum import StrEnum, auto

from pydantic import BaseModel


class UserStatus(StrEnum):
    active = auto()
    inactive = auto()


class UserBase(BaseModel):
    username: str
    email: str
    status: UserStatus = UserStatus.active


class UserCreate(UserBase):
    password: str
    check_password: str


class UserRead(UserBase):
    id: int


class UserUpdate(UserCreate):
    username: str | None = None
    email: str | None = None
    status: UserStatus | None = None
    password: str | None = None
    check_password: str | None = None
