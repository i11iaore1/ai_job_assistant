from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class PostgresConfig(BaseSettings):
    db_name: str = Field(validation_alias="PSQL_DB")
    user: str = Field(validation_alias="PSQL_USER")
    password: SecretStr = Field(validation_alias="PSQL_PASSWORD")
    host: str = Field(validation_alias="PSQL_HOST")
    port: int = Field(validation_alias="PSQL_PORT")

    model_config = SettingsConfigDict(extra="ignore")

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
