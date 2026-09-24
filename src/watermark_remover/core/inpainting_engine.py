import shutil
import subprocess
import sys
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path

from PySide6.QtCore import QRect
from PySide6.QtGui import QImage, qRgb


class InpaintingEngineError(Exception):
    """Error al procesar una imagen con el motor de inpainting."""


class InpaintingEngine(ABC):
    @abstractmethod
    def process(self, image_path: Path, mask_rect: QRect, output_path: Path) -> Path:
        """Procesa image_path removiendo la región mask_rect, guarda el resultado en output_path."""
        raise NotImplementedError


def _rect_to_mask_image(mask_rect: QRect, image_path: Path) -> QImage:
    source = QImage(str(image_path))
    if source.isNull():
        raise InpaintingEngineError(f"No se pudo leer la imagen: {image_path}")

    mask = QImage(source.size(), QImage.Format.Format_Grayscale8)
    mask.fill(qRgb(0, 0, 0))

    clamped = mask_rect.intersected(QRect(0, 0, source.width(), source.height()))
    for y in range(clamped.top(), clamped.bottom() + 1):
        for x in range(clamped.left(), clamped.right() + 1):
            mask.setPixel(x, y, qRgb(255, 255, 255))

    return mask


def _find_iopaint_executable() -> str:
    found = shutil.which("iopaint")
    if found:
        return found

    scripts_candidate = Path(sys.executable).parent / "Scripts" / "iopaint.exe"
    if scripts_candidate.exists():
        return str(scripts_candidate)

    raise InpaintingEngineError(
        "No se encontró el ejecutable de IOPaint. Instálalo con: pip install iopaint"
    )


class IOPaintEngine(InpaintingEngine):
    def __init__(self, model: str = "lama", device: str = "cpu"):
        self.model = model
        self.device = device

    def process(self, image_path: Path, mask_rect: QRect, output_path: Path) -> Path:
        if not image_path.exists():
            raise InpaintingEngineError(f"Imagen no encontrada: {image_path}")

        executable = _find_iopaint_executable()

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            mask_path = tmp_path / "mask.png"
            _rect_to_mask_image(mask_rect, image_path).save(str(mask_path))

            output_dir = tmp_path / "output"
            output_dir.mkdir()

            result = subprocess.run(
                [
                    executable, "run",
                    "--model", self.model,
                    "--device", self.device,
                    "--image", str(image_path),
                    "--mask", str(mask_path),
                    "--output", str(output_dir),
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                raise InpaintingEngineError(
                    f"IOPaint falló al procesar la imagen: {result.stderr[-500:] or result.stdout[-500:]}"
                )

            produced = output_dir / image_path.name
            if not produced.exists():
                raise InpaintingEngineError("IOPaint no generó el archivo de salida esperado.")

            output_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(produced, output_path)
            return output_path
