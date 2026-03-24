from pydantic import computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 配置来源
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 应用信息
    app_name: str = "PAWCARE"
    debug: bool = False

    # PostgreSQL 配置
    db_host: str = "example_host"
    db_port: int = 5432
    db_user: str = "example_user"
    db_password: str = "example_password"  # 放在 .env 或环境变量中
    db_name: str = "example_db"

    # 连接池配置
    pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_pre_ping: bool = True
    pool_recycle: int = 3600
    pool_use_lifo: bool = False
    echo: bool = False

    # JWT 配置（重要：请在 .env 或环境变量中设置真实的密钥，生产环境不能使用空值）
    jwt_secret: str = "example_jwt_secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Redis 配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    auth_redis_db: int = 0
    cache_redis_db: int = 1

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @computed_field
    @property
    def engine_options(self) -> dict:
        # 统一封装 engine options, 供 create_async_engine 使用
        return {
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "pool_timeout": self.pool_timeout,
            "pool_recycle": self.pool_recycle,
            "pool_use_lifo": self.pool_use_lifo,
            "echo": self.echo,
        }

    @computed_field
    @property
    def auth_redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.auth_redis_db}"

    @computed_field
    @property
    def cache_redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.cache_redis_db}"

    @model_validator(mode="after")
    def validate_sensitive_settings(self):
        if not self.jwt_secret or self.jwt_secret == "example_jwt_secret":
            raise ValueError(
                "jwt_secret 不可为空且不能为默认占位符，生产环境请通过 .env 或系统环境变量设置真实值。"
            )

        if not self.debug:
            missing_db = [
                name
                for name in ("db_user", "db_password", "db_host", "db_name")
                if not getattr(self, name)
            ]
            if missing_db:
                raise ValueError(
                    f"生产环境缺少数据库配置：{', '.join(missing_db)}，请在 .env 或环境变量中注入真实值。"
                )

        return self


settings = Settings()
