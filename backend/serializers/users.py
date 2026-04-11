from pydantic import BaseModel, EmailStr

from serializers.base_serializer import BaseDatedSerializer

# DTOs


class UserDBSchema(BaseDatedSerializer):
    """DTO for SAFE user DB record (no password_hash)"""

    id: int
    email: EmailStr
    username: str
    is_admin: bool


class UserProfileDBSchema(BaseDatedSerializer):
    """DTO for user profile DB record"""

    resume_file_path: str
    resume_text: str
    context: str


# registration


class RegistrationSerializer(BaseModel):
    """validates registration request payload"""

    email: EmailStr
    # if username not provided it is generated from email
    username: str | None = None
    password: str
    remember_me: bool  # determines whether refresh is sent as Session Cookie or Long living (Max-Age: 2592000)


class RegistrationResponseSerializer(UserDBSchema):
    """describes registration response payload structure"""

    pass


# login


class LoginSerializer(BaseModel):
    """validates login request payload"""

    email: EmailStr
    password: str
    remember_me: bool  # determines whether refresh is sent as Session Cookie or Long living (Max-Age: 2592000)


class LoginResponseSerializer(UserDBSchema):
    """describes login response payload structure"""

    # user might not have a profile yet
    profile_info: UserProfileDBSchema | None
