# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # 数据库
    database_url: str = "mysql+pymysql://root:123456@localhost/blog"
    redis_url: str = "redis://localhost:6379/0"

    # 安全
    secret_key: str                          # 必填，没有默认值，启动时必须有
    access_token_expire_minutes: int = 60 * 24
    algorithm: str = "HS256"

    # 应用
    debug: bool = False
    app_name: str = "Blog API"

    # CORS
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()