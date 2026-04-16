from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password_to_verify: str, password_hash: str) -> bool:
    return pwd_context.verify(password_to_verify, password_hash)
