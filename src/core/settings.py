from os import environ
from pathlib import Path

from pydantic import BaseModel, ConfigDict, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent
ENV_DIR = BASE_DIR / "env"
CERTS_DIR = BASE_DIR.parent / "certs"

environ.setdefault(
    "ENV_FILE",
    (ENV_DIR / "dev.env").absolute().as_posix(),
)


class DBSettings(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    drivername: str

    user: str | None = None
    password: str | None = None

    host: str | None = None
    port: int | str | None = None

    name: str

    echo_sql: bool = False
    echo_pool: bool = False
    max_overflow: int = 10
    pool_size: int = 5

    @field_validator("name")
    def db_name_validator(
        cls,
        value: str,
        info: ValidationInfo,
        **kwargs,
    ) -> str:
        if "sqlite" in info.data.get("drivername"):
            return (BASE_DIR.parent / "db" / value).absolute().as_posix()

        return value

    @field_validator(
        "user",
        "password",
        "host",
        "port",
    )
    def db_settings_validator(
        cls,
        value: str | int | None,
        info: ValidationInfo,
        **kwargs,
    ) -> str | int | None:
        if not value:
            if "postgresql" in info.data.get("drivername"):
                raise ValueError(f"`{info.field_name}` must be `set")

            return None

        if info.field_name == "port":
            return int(value)

        return value


class AuthSettings(BaseModel):
    certs_dir: Path | str = "certs"

    public_key: Path | str = "auth-jwt-public.pem"
    private_key: Path | str = "auth-jwt-private.pem"

    jwt_algorithm: str = "RS256"

    cookie_key: str = "sid"

    access_token_age: int = 7_200  # 2h

    @field_validator("certs_dir", mode="before")
    def certs_dir_validator(
        cls,
        value: str,
        info: ValidationInfo,
        **kwargs,
    ) -> Path:
        return BASE_DIR.parent / value

    @field_validator("public_key", "private_key")
    def certs_validator(
        cls,
        value: str,
        info: ValidationInfo,
        **kwargs,
    ) -> Path:
        return CERTS_DIR / value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="app.",
        env_file=(f"{ENV_DIR / '.env.template'}", environ["ENV_FILE"]),
        case_sensitive=False,
        arbitrary_types_allowed=True,
        env_nested_delimiter=".",
        env_file_encoding="UTF-8",
    )

    # ======================================|Main|====================================== #
    debug: bool = True

    base_dir: Path = BASE_DIR
    base_encoding: str = "UTF-8"

    api_name: str
    api_version: str

    host: str
    port: int

    origins: list[str]

    reverse_proxy: bool = False

    public_key: Path | str = "public.pem"
    private_key: Path | str = "private.pem"

    @field_validator("public_key", "private_key")
    def certs_validator(
        cls,
        value: str,
        info: ValidationInfo,
        **kwargs,
    ) -> Path:
        return CERTS_DIR / value

    # ====================================|Database|==================================== #
    db: DBSettings
    # =================================|Authentication|================================= #
    auth: AuthSettings


settings = Settings()
