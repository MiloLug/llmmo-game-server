from functools import cache
from llmmo.config.spec import Config


@cache
def config() -> Config:
    config = Config()
    config.db.base_path.mkdir(parents=True, exist_ok=True)
    return config
