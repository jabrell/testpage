import boto3
import pytest
from moto import mock_aws

from app.filestorage import S3FileStorage


@pytest.fixture
def s3_storage():
    # Mock S3 bucket
    with mock_aws():
        s3_client = boto3.client("s3", region_name="us-east-1")
        bucket_name = "test-bucket"
        s3_client.create_bucket(Bucket=bucket_name)

        yield S3FileStorage(
            bucket_name=bucket_name,
            aws_access_key_id="fake_access_key",
            aws_secret_access_key="fake_secret_key",
        )


def test_save_and_load(s3_storage: S3FileStorage):
    key = "test_file.txt"
    data = b"Hello, World!"

    # Save data
    _ = s3_storage.save(key, data)

    # Load data
    loaded_data = s3_storage.load(key)

    # Check if loaded data matches saved data
    assert loaded_data == data


def test_delete(s3_storage: S3FileStorage):
    key = "test_file.txt"
    data = b"Hello, World!"

    # Save data
    s3_storage.save(key, data)

    # Delete file
    result = s3_storage.delete(key)

    # Check if delete was successful
    assert result

    # Check if file no longer exists
    assert not s3_storage.exists(key)


def test_exists(s3_storage: S3FileStorage):
    key = "test_file.txt"
    data = b"Hello, World!"

    # Save data
    s3_storage.save(key, data)

    # Check if file exists
    assert s3_storage.exists(key)

    # Delete file
    s3_storage.delete(key)

    # Check if file no longer exists
    assert not s3_storage.exists(key)


def test_list(s3_storage: S3FileStorage):
    # Save multiple files
    s3_storage.save("file1.txt", b"Content 1")
    s3_storage.save("file2.txt", b"Content 2")

    # List files in the bucket
    files = s3_storage.list()

    # Check if listed files match saved files
    assert "file1.txt" in files
    assert "file2.txt" in files


def test_load_nonexistent_file(s3_storage: S3FileStorage):
    key = "nonexistent_file.txt"

    # Attempt to load a non-existent file
    with pytest.raises(FileNotFoundError):
        s3_storage.load(key)


def test_delete_nonexistent_file(s3_storage: S3FileStorage):
    key = "nonexistent_file.txt"

    # Attempt to delete a non-existent file
    result = s3_storage.delete(key)

    # Check if delete returns False
    assert not result


def test_invalid_credentials():
    # Attempt to create S3FileStorage with invalid credentials
    with pytest.raises(Exception, match="AWS credentials not available"):
        st = S3FileStorage(
            bucket_name="test-bucket",
            aws_access_key_id="invalid_key",
            aws_secret_access_key="invalid_secret",
            region_name="us-east-1",
        )
        st.save("test_file.txt", b"Hello, World!")
