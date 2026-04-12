from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())")
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())")
    )

    def __repr__(self) -> str:
        columns = [
            f"{column_name}={getattr(self, column_name)}"
            for column_name in self.__table__.columns.keys()
        ]
        return f"<{self.__class__.__name__} {', '.join(columns)}>"
