from pydantic import BaseModel, EmailStr

from serializers.base_serializer import BaseDatedSerializer

# DTOs


class CreateUserSchema(BaseModel):
    """DTO for creating a user DB record"""

    email: EmailStr
    # if username not provided it is generated from email
    username: str | None = None
    password: str
    is_admin: bool = False


class UserDBSchema(BaseDatedSerializer):
    """DTO for SAFE user DB record (no password_hash)"""

    id: int
    email: EmailStr
    username: str
    is_admin: bool


class CreateUserProfileSchema(BaseModel):
    """DTO for creating a user profile DB record"""

    resume_file_path: str
    resume_text: str
    context: str


class UserProfileDBSchema(CreateUserProfileSchema, BaseDatedSerializer):
    """DTO for user profile DB record"""

    pass


class FullUserInfoSchema(UserDBSchema):
    """DTO for full user info including profile DB record"""

    # user might not have a profile yet
    profile: UserProfileDBSchema | None


class UserCredentialsSchema(BaseModel):
    """DTO for user credentials"""

    email: EmailStr
    password: str


# registration


class RegistrationSerializer(UserCredentialsSchema):
    """validates registration request payload"""

    # if username not provided it is generated from email
    username: str | None = None
    remember_me: bool  # determines whether refresh is sent as Session Cookie or Long living (Max-Age: 2592000)


# login


class LoginSerializer(UserCredentialsSchema):
    """validates login request payload"""

    remember_me: bool  # determines whether refresh is sent as Session Cookie or Long living (Max-Age: 2592000)
