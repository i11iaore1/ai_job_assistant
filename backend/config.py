from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    GROQ_API_KEY: SecretStr
    JWT_SECRET_KEY: SecretStr

    model_config = SettingsConfigDict(env_file="env/.env", extra="ignore")


app_config = AppConfig()  # type: ignore
