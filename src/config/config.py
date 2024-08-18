from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5433/contacts"
    secret_key: str = "secret_key"
    algorithm: str = "HS256"
    mail_username: str = "postgres@meail.com"
    mail_password: str = "postgres"
    mail_from: str = "postgres"
    mail_port: int = 567234
    mail_server: str = "postgres"
    redis_host: str = 'localhost'
    redis_port: int = 6379
    cloudinary_name: str = 'abc'
    cloudinary_api_key: str = '326488457974591'
    cloudinary_api_secret: str = "secret"

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"
    )


config = Settings()
