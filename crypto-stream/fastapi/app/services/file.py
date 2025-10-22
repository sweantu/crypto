from typing import Annotated

from fastapi import Depends

from app.core.file import FileUpload, upload_file


class FileService:
    def upload_files(self, files_upload: list[FileUpload]) -> list[str]:
        return [
            upload_file(content=file.content, filename=file.filename)
            for file in files_upload
        ]


def get_file_service() -> FileService:
    return FileService()


FileServiceDep = Annotated[FileService, Depends(get_file_service)]
