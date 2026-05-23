from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class RabbitMQConfig(BaseSettings):
    user: str = Field(validation_alias="RABBITMQ_USER")
    password: SecretStr = Field(validation_alias="RABBITMQ_PASSWORD")
    host: str = Field(validation_alias="RABBITMQ_HOST")
    port: str = Field(validation_alias="RABBITMQ_PORT")

    model_config = SettingsConfigDict(extra="ignore")

    @property
    def broker_DSN(self) -> str:
        return f"amqp://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}//"


rabbitmq_config = RabbitMQConfig()  # type: ignore

BROKER_DSN = rabbitmq_config.broker_DSN
