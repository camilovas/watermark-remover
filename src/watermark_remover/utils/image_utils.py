from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QImage, QPixmap

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def is_supported_format(path: str | Path) -> bool:
    return Path(path).suffix.lower() in SUPPORTED_EXTENSIONS


def make_thumbnail(path: str | Path, max_size: int = 128) -> QPixmap:
    image = QImage(str(path))
    if image.isNull():
        raise ValueError(f"No se pudo leer la imagen: {path}")
    scaled = image.scaled(
        QSize(max_size, max_size), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
    )
    return QPixmap.fromImage(scaled)
