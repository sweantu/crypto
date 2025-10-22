from fastapi import APIRouter

from app.core.file import ImagesUploadDep
from app.services.file import FileServiceDep

router = APIRouter()


@router.post("/upload-images/", response_model=list[str])
def upload_images(images_upload: ImagesUploadDep, file_service: FileServiceDep):
    urls = file_service.upload_files(images_upload)
    return urls
