import os
import tempfile
from collections.abc import Generator

import pytest

# Assuming the LocalFileStorage class is defined in a module named storage
from app.filestorage import LocalFileStorage


@pytest.fixture
def storage() -> Generator[LocalFileStorage, None, None]:
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        yield LocalFileStorage(base_path=temp_dir)


def test_save_and_load(storage: LocalFileStorage):
    key = "test_file.txt"
    data = b"Hello, World!"

    # Save data
    file_path = storage.save(key, data)

    # Check if file exists
    assert os.path.exists(storage._get_file_path(file_path))

    # Load data
    loaded_data = storage.load(key)

    # Check if loaded data matches saved data
    assert loaded_data == data


def test_load_not_found(storage: LocalFileStorage):
    key = "non_existent_file.txt"
    with pytest.raises(FileNotFoundError):
        storage.load(key)


def test_delete(storage: LocalFileStorage):
    key = "test_file.txt"
    data = b"Hello, World!"

    # Save data
    storage.save(key, data)

    # Delete file
    result = storage.delete(key)

    # Check if delete was successful
    assert result

    # Check if file no longer exists
    assert not storage.exists(key)

    # Delete non-existent file
    assert not storage.delete(key)


def test_exists(storage: LocalFileStorage):
    key = "test_file.txt"
    data = b"Hello, World!"

    # Save data
    storage.save(key, data)

    # Check if file exists
    assert storage.exists(key)

    # Delete file
    storage.delete(key)

    # Check if file no longer exists
    assert not storage.exists(key)


def test_list(storage: LocalFileStorage):
    # Save multiple files
    storage.save("file1.txt", b"Content 1")
    storage.save("file2.txt", b"Content 2")

    # List files in the base directory
    files = storage.list()
    # Check if listed files match saved files
    assert "file1.txt" in files
    assert "file2.txt" in files
