from pydantic_settings import BaseSettings
from pydantic import Field, BaseModel
from pathlib import Path
from fastapi_csrf_protect import CsrfProtect


BASE_DIR = Path(__file__).resolve().parent.parent

ENV_PATH = BASE_DIR / ".env"

class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt_private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt_public.pem"
    access_token_expire_minutes: str = 30
    refresh_token_expire_days: str = 30
    algorithm: str = "RS256"


class Cookies(BaseModel):
    access_cookie_name: str = "access_token"
    refresh_cookie_name: str = "refresh_token"
    cookie_params: dict = {
        "httponly": True,
        "secure": True,
        "samesite": "lax",
        "path": "/",
    }


class Settings(BaseSettings):
    postgres_host: str = Field(..., env="POSTGRES_HOST")
    postgres_port: int = Field(..., env="POSTGRES_PORT")
    postgres_db: str = Field(..., env="POSTGRES_DB")
    postgres_user: str = Field(..., env="POSTGRES_USER")
    postgres_password: str = Field(..., env="POSTGRES_PASSWORD")

    csrf_token: str = Field(..., env="CSRF_TOKEN")

    auth_jwt: AuthJWT = AuthJWT()
    cookies: Cookies = Cookies()

    media_dir: Path = Path("media")
    avatar_dir: Path = media_dir / "avatars"
    avatar_dir_prefix: str = "/media/avatars/"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    class Config:
        env_file = ENV_PATH
        env_file_encoding = "utf-8"


settings = Settings()

class CsrfSettings(BaseSettings):
    secret_key: str = settings.csrf_token
    cookie_samesite: str = "lax"
    cookie_key: str = "csrftoken"
    header_name: str = "x-csrf-token"


@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()
