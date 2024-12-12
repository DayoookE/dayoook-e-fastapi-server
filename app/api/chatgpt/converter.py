from io import BytesIO

from fastapi import UploadFile


def bytesio_to_uploadfile(byte_data: bytes, filename: str) -> UploadFile:
    file_like = BytesIO(byte_data)  # BytesIO 객체 생성
    file_like.name = filename  # 파일명 지정

    # FastAPI에서 사용하는 UploadFile처럼 동작하는 객체 생성
    upload_file = UploadFile(file=file_like, filename=filename)
    return upload_file
