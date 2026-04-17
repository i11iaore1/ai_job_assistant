from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    def __repr__(self) -> str:
        columns = [
            f"{column_name}={getattr(self, column_name)}"
            for column_name in self.__table__.columns.keys()
        ]
        return f"<{self.__class__.__name__} {', '.join(columns)}>"
