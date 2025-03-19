from typing import Any

import boto3
from mypy_boto3_s3.client import S3Client


class S3FileStorage:
    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str = "us-east-1",
    ):
        self.bucket_name = bucket_name
        self.s3_client: S3Client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )

    def save(self, key: Any, data: bytes) -> str:
        """Save the data to the bucket with the given key.

        Args:
            key (Any): The key to save the data with.
            data (bytes): The data to save.

        Returns:
            str: The key the data was saved with.

        Raises:
            Exception: If AWS credentials are not available.
        """
        try:
            self.s3_client.put_object(Bucket=self.bucket_name, Key=str(key), Body=data)
            return key
        except self.s3_client.exceptions.ClientError:
            raise Exception("AWS credentials not available") from None

    def load(self, key: Any) -> bytes:
        """Load the data from the bucket with the given key.

        Args:
            key (Any): The key to load the data from.

        Returns:
            bytes: The data loaded from the bucket.

        Raises:
            FileNotFoundError: If the key does not exist in the bucket.
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=str(key))
            return response["Body"].read()
        except self.s3_client.exceptions.ClientError:
            raise FileNotFoundError(
                f"The key {key} does not exist in the bucket"
            ) from None

    def delete(self, key: Any) -> bool:
        """Delete the key from the bucket.

        Args:
            key (Any): The key to delete.

        Returns:
            bool: True if the key was deleted, False otherwise.
        """
        if not self.exists(key):
            return False
        else:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=str(key))
            return True

    def exists(self, key: Any) -> bool:
        """Check if the key exists in the bucket.

        Args:
            key (Any): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=str(key))
            return True
        except self.s3_client.exceptions.ClientError:
            return False

    def list(self, prefix: str = "") -> list[str]:
        """
        List all keys in the bucket with the given prefix.

        Args:
            prefix (str): The prefix to filter keys by.

        Returns:
            list[str]: The list of keys in the bucket with the given prefix.
        """
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name, Prefix=prefix
        )
        if "Contents" in response:
            return [item["Key"] for item in response["Contents"]]
        return []  # pragma: no cover
