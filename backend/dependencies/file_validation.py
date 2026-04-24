from typing import Annotated

from fastapi import Depends, File, UploadFile

from exceptions.file_validation import FileTooBig, InvalidFileExtension

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
VALID_CONTENT_TYPES = ["application/pdf"]


def validate_resume_file(file: UploadFile) -> UploadFile:
    if file is not None:
        if file.content_type not in VALID_CONTENT_TYPES:
            raise InvalidFileExtension()

        if file.size is not None and file.size > MAX_FILE_SIZE:
            raise FileTooBig()

    return file


def validate_resume_file_if_not_none[T: (UploadFile | None)](file: T = File(None)) -> T:
    if file is None:
        return file
    return validate_resume_file(file)


ResumeFileDependency = Annotated[UploadFile, Depends(validate_resume_file)]
OptionalResumeFileDependency = Annotated[
    UploadFile | None, Depends(validate_resume_file_if_not_none)
]
