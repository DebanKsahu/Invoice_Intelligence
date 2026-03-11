from enum import Enum
from pathlib import Path


class DirectoryPaths(Enum):
    BASE_DIR = Path(__file__).resolve().parents[2]
    APP_DIR = Path(__file__).resolve().parents[1]
    UPLOAD_DIR = Path(__file__).resolve().parents[1] / "localStorage"