import os
import tomllib
from typing import Any

from pydantic import BaseModel, SecretStr

DEFAULT_CONFIG_PATH = "./config/config.toml"


class RabbitConfig(BaseModel):
    user: str
    password: str
    port: int = 5672
    host: str = "localhost"

    @property
    def url(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/"


class Telegram(BaseModel):
    bot_token: SecretStr


class TraceConfig(BaseModel):
    otlp_endpoint: str


class Config(BaseModel):
    rabbit: RabbitConfig
    trace: TraceConfig
    telegram: Telegram


def read_toml(path: str) -> dict[str, Any]:
    with open(path, "rb") as f:
        return tomllib.load(f)


def load_config() -> Config:
    path = os.getenv("CONFIG_PATH", DEFAULT_CONFIG_PATH)
    data = read_toml(path)
    return Config.model_validate(data)
