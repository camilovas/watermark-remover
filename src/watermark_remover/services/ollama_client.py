import base64
import io

import requests
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QImage

from watermark_remover.services.config import get_ollama_host, get_ollama_model

THUMBNAIL_MAX_SIDE = 512
REQUEST_TIMEOUT_SECONDS = 180

DETECTION_PROMPT = (
    "This image may contain a watermark, logo, or text overlay. "
    "If you see one, respond ONLY with compact JSON: "
    '{"found": true, "box": [x_min, y_min, x_max, y_max]} '
    "using normalized coordinates (0.0 to 1.0) relative to this image's width/height. "
    'If there is none, respond {"found": false}. No extra text.'
)


class OllamaUnavailableError(Exception):
    """Ollama no está disponible (no responde en el host configurado)."""


class OllamaClient:
    def __init__(self, host: str | None = None, model: str | None = None):
        self.host = host or get_ollama_host()
        self.model = model or get_ollama_model()

    def is_available(self) -> bool:
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=3)
            return resp.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def _thumbnail_base64(self, image_path) -> str:
        image = QImage(str(image_path))
        if image.isNull():
            raise ValueError(f"No se pudo leer la imagen: {image_path}")

        scaled = image.scaled(
            QSize(THUMBNAIL_MAX_SIDE, THUMBNAIL_MAX_SIDE),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        buffer = io.BytesIO()
        # QImage no puede guardar directo en BytesIO; se guarda a través de QBuffer.
        from PySide6.QtCore import QBuffer, QIODevice

        qbuffer = QBuffer()
        qbuffer.open(QIODevice.OpenModeFlag.WriteOnly)
        scaled.save(qbuffer, "PNG")
        return base64.b64encode(bytes(qbuffer.data())).decode()

    def detect_watermark_region(self, image_path) -> str:
        """Envía una miniatura al modelo de visión y devuelve la respuesta cruda (texto)."""
        image_b64 = self._thumbnail_base64(image_path)

        try:
            resp = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": DETECTION_PROMPT,
                    "images": [image_b64],
                    "stream": False,
                    # Forzado a CPU: bug conocido de GPU/Vulkan en algunas instalaciones de
                    # Ollama en Windows (ver docs/research/best_practices.md, spike HU-3).
                    "options": {"num_gpu": 0},
                },
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.exceptions.RequestException as exc:
            raise OllamaUnavailableError(f"Ollama no respondió en {self.host}: {exc}") from exc

        if resp.status_code != 200:
            raise OllamaUnavailableError(f"Ollama devolvió error {resp.status_code}: {resp.text[:200]}")

        return resp.json().get("response", "")
