import json
import re
from abc import ABC, abstractmethod
from pathlib import Path

from PySide6.QtCore import QRect
from PySide6.QtGui import QImage

from watermark_remover.services.ollama_client import OllamaClient, OllamaUnavailableError

_NUMBER_LIST_RE = re.compile(r"[-+]?\d*\.?\d+")


class WatermarkDetector(ABC):
    @abstractmethod
    def detect(self, image_path: Path) -> QRect | None:
        """Intenta detectar la región de una marca de agua. None si no se detecta o no aplica."""
        raise NotImplementedError


class NullDetector(WatermarkDetector):
    """Se usa cuando Ollama no está disponible. Nunca hace red, nunca falla."""

    def detect(self, image_path: Path) -> QRect | None:
        return None


def _parse_box(raw_response: str) -> tuple[float, float, float, float] | None:
    text = raw_response.strip()

    try:
        data = json.loads(text)
        if isinstance(data, dict):
            if data.get("found") is False:
                return None
            box = data.get("box")
            if box and len(box) == 4:
                return tuple(float(v) for v in box)
        elif isinstance(data, list) and len(data) == 4:
            return tuple(float(v) for v in data)
    except (json.JSONDecodeError, TypeError, ValueError):
        pass

    # Fallback tolerante: algunos modelos de visión ignoran el formato pedido
    # y devuelven solo una lista de 4 números (con o sin corchetes/JSON).
    numbers = _NUMBER_LIST_RE.findall(text)
    if len(numbers) >= 4:
        return tuple(float(n) for n in numbers[:4])

    return None


def _box_to_rect(box: tuple[float, float, float, float], image_width: int, image_height: int) -> QRect:
    x_min, y_min, x_max, y_max = box
    # Si todos los valores caben en [0, ~1.5] se asume normalizado (0.0-1.0); si no, píxeles directos.
    normalized = max(box) <= 1.5
    if normalized:
        x_min, x_max = x_min * image_width, x_max * image_width
        y_min, y_max = y_min * image_height, y_max * image_height

    x_min, x_max = sorted((x_min, x_max))
    y_min, y_max = sorted((y_min, y_max))
    return QRect(int(x_min), int(y_min), max(1, int(x_max - x_min)), max(1, int(y_max - y_min)))


class OllamaWatermarkDetector(WatermarkDetector):
    def __init__(self, client: OllamaClient | None = None):
        self.client = client or OllamaClient()

    def is_available(self) -> bool:
        return self.client.is_available()

    def detect(self, image_path: Path) -> QRect | None:
        try:
            raw_response = self.client.detect_watermark_region(image_path)
        except OllamaUnavailableError:
            return None

        box = _parse_box(raw_response)
        if box is None:
            return None

        image = QImage(str(image_path))
        if image.isNull():
            return None

        return _box_to_rect(box, image.width(), image.height())


def create_detector(client: OllamaClient | None = None) -> WatermarkDetector:
    """Factory: devuelve un detector real de Ollama si está disponible, si no, NullDetector."""
    ollama_detector = OllamaWatermarkDetector(client)
    if ollama_detector.is_available():
        return ollama_detector
    return NullDetector()
