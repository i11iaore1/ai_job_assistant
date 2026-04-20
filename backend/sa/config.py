from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class PostgresConfig(BaseSettings):
    db_name: str = Field(validation_alias="POSTGRES_DB")
    user: str = Field(validation_alias="POSTGRES_USER")
    password: SecretStr = Field(validation_alias="POSTGRES_PASSWORD")
    host: str = Field(validation_alias="PG_HOST", default="localhost")
    port: int = Field(validation_alias="PG_EXT_PORT")

    model_config = SettingsConfigDict(
        env_file=(".env", "env/postgres.env", "env/app.env"), extra="ignore"
    )

    def _get_DSN(self, driver: str) -> str:
        return URL.create(
            drivername=f"postgresql+{driver}",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            database=self.db_name,
        ).render_as_string(hide_password=False)

    @property
    def DSN_psycopg(self):
        return self._get_DSN(driver="psycopg")

    @property
    def DSN_asyncpg(self):
        return self._get_DSN(driver="asyncpg")


pg_config = PostgresConfig()  # type: ignore

CURRENT_DSN = pg_config.DSN_psycopg
