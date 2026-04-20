from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    groq_api_key: SecretStr = Field(validation_alias="GROQ_API_KEY")
    jwt_secret: SecretStr = Field(validation_alias="JWT_SECRET_KEY")

    model_config = SettingsConfigDict(env_file="env/app.env", extra="ignore")


app_config = AppConfig()  # type: ignore
