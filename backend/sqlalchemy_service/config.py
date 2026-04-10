from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class PostgresConfig(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    model_config = SettingsConfigDict(env_file="env/postgres.env", extra="ignore")

    def _get_DSN(self, driver: str) -> str:
        return URL.create(
            drivername=f"postgresql+{driver}",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD.get_secret_value(),
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        ).render_as_string(hide_password=False)

    @property
    def DSN_psycopg(self):
        return self._get_DSN(driver="psycopg")

    @property
    def DSN_asyncpg(self):
        return self._get_DSN(driver="asyncpg")


pg_config = PostgresConfig()  # type: ignore
