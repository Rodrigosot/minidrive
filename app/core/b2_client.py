import boto3
from mypy_boto3_s3 import S3Client
from botocore.client import Config
from app.core.config import settings

# Crear cliente S3 apuntando a Backblaze B2
s3: S3Client = boto3.client(
    "s3",
    endpoint_url=f"https://{settings.B2_ENDPOINT_URL}",
    aws_access_key_id=settings.B2_KEYID,
    aws_secret_access_key=settings.B2_APPLICATIONKEY,
    config=Config(signature_version="s3v4")
)

