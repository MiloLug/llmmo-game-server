from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict, BaseSettings


class RunConfig(BaseModel):
    host: str = "localhost"
    port: int = 8000


class CORSConfig(BaseModel):
    origins: list[str]
    credentials: bool = True
    methods: list[str] = Field(default_factory=lambda: ["*"])
    headers: list[str] = Field(default_factory=lambda: ["*"])


class DBConfig(BaseModel):
    base_path: Path = Path(".state")


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_prefix="BACKEND__",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )

    run: RunConfig
    cors: CORSConfig
    db: DBConfig
