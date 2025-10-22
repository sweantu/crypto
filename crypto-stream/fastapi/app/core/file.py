from io import BytesIO
from typing import Annotated, NamedTuple
from uuid import uuid4

import boto3
from botocore.exceptions import NoCredentialsError
from fastapi import Depends, File, HTTPException, UploadFile


class FileUpload(NamedTuple):
    content: bytes
    filename: str


def upload_file(content: bytes, filename: str) -> str:
    s3 = boto3.client("s3")
    file_obj = BytesIO(content)
    bucket_name = "survey-backend-bucket"
    key = f"uploads/{filename}"

    try:
        s3.upload_fileobj(file_obj, bucket_name, key)
        url = f"https://{bucket_name}.s3.ap-southeast-1.amazonaws.com/{key}"
        return url
    except NoCredentialsError as e:
        raise HTTPException(status_code=500, detail="No AWS credentials found") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}") from e


def get_images_upload(
    files: Annotated[list[UploadFile], File(...)],
) -> list[FileUpload]:
    result: list[FileUpload] = []
    for file in files:
        if (
            not file.content_type
            or not file.content_type.startswith("image/")
            or not file.filename
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image file: {file.filename if file.filename else 'unknown'}",
            )

        ext = file.filename.split(".")[-1]
        filename = f"{uuid4().hex}.{ext}"
        content = file.file.read()
        result.append(FileUpload(content=content, filename=filename))

    return result


ImagesUploadDep = Annotated[list[FileUpload], Depends(get_images_upload)]
