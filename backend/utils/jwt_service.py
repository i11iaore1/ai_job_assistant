from typing import Any

import jwt

from config import app_config

JWT_SECRET_KEY = app_config.jwt_secret.get_secret_value()

ALGORITHM = "HS256"


def jwt_encode(payload: dict[str, Any]) -> str:
    return jwt.encode(payload, key=JWT_SECRET_KEY, algorithm=ALGORITHM)


def jwt_decode(token: str, verify_exp: bool = True) -> dict[str, Any]:
    return jwt.decode(
        token,
        key=JWT_SECRET_KEY,
        algorithms=ALGORITHM,
        options={"verify_exp": verify_exp},
    )
