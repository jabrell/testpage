from pathlib import Path
from typing import Any


class LocalFileStorage:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, key: Any, data: bytes) -> str:
        file_path = self._get_file_path(key)
        with file_path.open("wb") as f:
            f.write(data)
        return str(file_path)

    def load(self, key: Any) -> bytes:
        file_path = self._get_file_path(key)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        with file_path.open("rb") as f:
            return f.read()

    def delete(self, key: Any) -> bool:
        file_path = self._get_file_path(key)
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def exists(self, key: Any) -> bool:
        file_path = self._get_file_path(key)
        return file_path.exists()

    def list(self) -> list[str]:
        return [p.name for p in self.base_path.iterdir()]

    def _get_file_path(self, key: Any) -> Path:
        return self.base_path / str(key)
