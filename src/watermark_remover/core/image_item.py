from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path

from PySide6.QtCore import QRect


class ImageStatus(Enum):
    LOADED = auto()
    MASK_SET = auto()
    PROCESSING = auto()
    DONE = auto()
    ERROR = auto()


@dataclass
class ImageItem:
    path: Path
    status: ImageStatus = ImageStatus.LOADED
    mask_rect: QRect | None = None
    result_path: Path | None = None
    error_message: str | None = field(default=None)

    @property
    def name(self) -> str:
        return self.path.name
