import os
from typing import Any

import jwt
from dotenv import load_dotenv

load_dotenv("env/.env")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

ALGORITHM = "HS256"


def jwt_encode(payload: dict[str, Any]) -> str:
    return jwt.encode(payload, key=JWT_SECRET_KEY, algorithm=ALGORITHM)


def jwt_decode(token: str) -> dict[str, Any]:
    return jwt.decode(token, key=JWT_SECRET_KEY, algorithms=ALGORITHM)
