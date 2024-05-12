import sys

from dotenv import dotenv_values
from loguru import logger
from pydantic import BaseSettings

config = dotenv_values(".env")


class CommonSettings(BaseSettings):
    APP_NAME: str = "Synth-Search"
    DEBUG_MODE: bool = True
    VERSION: str = "0.0.1"


class ServerSettings(BaseSettings):
    HOST: str = "localhost"
    PORT: int = 8000
    workers: int = 4


class LLMSettings(BaseSettings):
    LLM_MODEL_NAME: str = "llama3"
    LLM_TEMPERATURE: float = 0.1
    LLM_BASE_URL: str = ""


class MongoDBSettings(BaseSettings):
    DB_URL: str = config.get("DB_URL")


class Settings(CommonSettings, ServerSettings, LLMSettings, MongoDBSettings):
    @staticmethod
    def configure_logging(logger_name: str, log_file_name: str = "logs"):
        log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

        logger.remove()

        logger.add(
            f"{log_file_name}/{logger_name}.log",
            rotation="500 MB",
            level="INFO",
            format=log_format,
            retention=100,
            compression="zip",
        )

        logger.add(sys.stderr, level="INFO", format=log_format)

        return logger


settings = Settings()
