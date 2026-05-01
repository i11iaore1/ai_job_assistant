from sa.models import UserProfileModel
from sa.repositories.base import BaseRepository


class UserProfileRepository(BaseRepository[UserProfileModel]):
    def __init__(self) -> None:
        super().__init__(
            model=UserProfileModel,
            updatable_fields={"resume_file_path", "resume_text", "context"},
        )


user_profile_repository = UserProfileRepository()
