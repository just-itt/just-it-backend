import boto3
from ninja import UploadedFile

from justit import settings


class S3ImgUploader:
    def upload(self, domain: str, file: UploadedFile):
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
        )

        s3_client.upload_fileobj(
            file,
            settings.AWS_STORAGE_BUCKET_NAME,
            f"{domain}/{file.name}",
            ExtraArgs={"ACL": "public-read", "ContentType": file.content_type},
        )
        return f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/{domain}/{file.name}"

    def delete(self, file_path: str):
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
        )

        file_key = file_path.split(
            f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com"
        )[1]
        s3_client.delete_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key.strip("/")
        )
        return True
