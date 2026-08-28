from pathlib import Path
from app.config import config
from shared.logging.logger import configure_logging

logger = configure_logging(__name__)


class FilesystemService:

    def __init__(self):
        self.allowed_directory = Path(config.ALLOWED_DIRECTORY).resolve()

    def list_directory(self, path: str = ".") -> list[str]:
        directory = self._resolve_path(path)

        if not directory.is_dir():
            raise ValueError(f"'{path}' no es un directorio")

        logger.info(f"list diectory path = {directory}")

        return [
            item.name
            for item in directory.iterdir()
        ]

    def read_file(self, path: str) -> str:
        file_path = self._resolve_path(path)

        if not file_path.is_file():
            raise ValueError(f"'{path}' no es un archivo")

        logger.info(f"read_file path = {file_path}")
        
        return file_path.read_text(encoding="utf-8")

    def _resolve_path(self, path: str) -> Path:
        requested_path = Path(path)

        if requested_path.is_absolute():
            resolved_path = requested_path.resolve()
        else:
            resolved_path = (self.allowed_directory / requested_path).resolve()

        try:
            resolved_path.relative_to(self.allowed_directory)
        except ValueError:
            raise ValueError(
                f"Path fuera del directorio permitido: '{path}'"
            )

        return resolved_path