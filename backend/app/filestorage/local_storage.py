from pathlib import Path
from typing import Any


class LocalFileStorage:
    def __init__(self, base_path: str):
        """Initialize the LocalFileStorage with the given base path.

        Args:
            base_path (str): The base path to store the files.
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, key: Any, data: bytes) -> str:
        """Save the data to a file with the given key.

        Args:
            key (Any): The key to save the data with.
            data (bytes): The data to save.

        Returns:
            str: The key the data was saved with.
        """
        file_path = self._get_file_path(key)
        with file_path.open("wb") as f:
            f.write(data)
        return str(key)

    def load(self, key: Any) -> bytes:
        """Load the data from the file with the given key.

        Args:
            key (Any): The key to load the data

        Returns:
            bytes: The data loaded from the file

        Raises:
            FileNotFoundError: If the file does not exist
        """
        file_path = self._get_file_path(key)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        with file_path.open("rb") as f:
            return f.read()

    def delete(self, key: Any) -> bool:
        """Delete the file with the given key.

        Args:
            key (Any): The key to delete

        Returns:
            bool: True if the file was deleted, False otherwise
        """
        file_path = self._get_file_path(key)
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def exists(self, key: Any) -> bool:
        """Check if the file with the given key exists.

        Args:
            key (Any): The key to check

        Returns:
            bool: True if the file exists, False otherwise
        """
        file_path = self._get_file_path(key)
        return file_path.exists()

    def list(self) -> list[str]:
        """List all the keys in the storage.

        Returns:
            list[str]: The list of keys in the storage.
        """
        return [p.name for p in self.base_path.iterdir()]

    def _get_file_path(self, key: Any) -> Path:
        """Get the file path for the given key.

        Args:
            key (Any): The key to get the file path for.
        """
        return self.base_path / str(key)
