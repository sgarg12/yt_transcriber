
import io
from datetime import timedelta

from minio import Minio

from settings import settings


class Storage:
    def __init__(self) -> None:
        self.client = Minio(
            settings.storage_endpoint,
            access_key=settings.storage_access_key,
            secret_key=settings.storage_secret_key,
        )

    def ensure_bucket(self, bucket_name: str):
        bucket_exists = self.client.bucket_exists(bucket_name)
        if not bucket_exists:
            self.client.make_bucket(bucket_name)

    def upload_text(self, text: str, object_name: str, bucket_name: str):
        self.ensure_bucket(bucket_name)

        encoded_txt = text.encode('utf-8')
        data = io.BytesIO(encoded_txt)
        data.seek(0)
        data_length = len(encoded_txt)

        self.client.put_object(
            bucket_name,
            object_name,
            data,
            length=data_length
        )

    def get_presigned_url(
        self,
        object_name: str,
        bucket_name: str,
        *,
        expires: timedelta = timedelta(days=7)
    ) -> str:
        return self.client.presigned_get_object(
            bucket_name, object_name, expires=expires
        )