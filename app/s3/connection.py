import io
import os
import uuid

import boto3
import requests
from fastapi import APIRouter, UploadFile

secret_key = os.getenv("AWS_S3_SECRET_KEY")
access_key = os.getenv("AWS_S3_ACCESS_KEY")

s3 = boto3.client(
    "s3",
    aws_access_key_id=access_key,  # 본인 소유의 키를 입력
    aws_secret_access_key=secret_key,  # 본인 소유의 키를 입력
    region_name="ap-northeast-2"
)


def upload_to_s3(file: io.BytesIO, bucket_name: str, object_name: str):
    s3.upload_fileobj(
        file,
        bucket_name,
        object_name,
    )

    return f"https://{bucket_name}.s3.ap-northeast-2.amazonaws.com/{object_name}"


def download_from_s3(url: str):
    response = requests.get(url)
    return response.content
