import io
import os
import shutil
import subprocess
import sys
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFilter
from PySide6.QtCore import QBuffer, QIODevice, QRect
from PySide6.QtGui import QImage, qRgb

# Margen de difuminado alrededor del borde de la máscara al combinar el resultado con la
# imagen original, como fracción del lado menor de la máscara. Sin esto, LaMa/migan suelen
# dejar una costura visible (un borde duro alrededor de la zona reconstruida) — ver hallazgo
# documentado en docs/research/best_practices.md tras probar con una imagen real.
FEATHER_FRACTION = 0.15
FEATHER_MIN_PX = 6
FEATHER_MAX_PX = 60

SERVER_REQUEST_TIMEOUT_SECONDS = 120


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


def _qimage_to_bytes(image: QImage, fmt: str = "PNG") -> bytes:
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, fmt)
    return bytes(buffer.data())


def _feather_blend(original_path: Path, inpainted_bytes: bytes, mask_rect: QRect, output_path: Path):
    """Combina el resultado del motor con la imagen original usando una máscara con
    bordes difuminados (Gaussian blur), en vez de pegar el parche con un borde duro.
    Reduce mucho la "costura" visible alrededor de la zona reconstruida."""
    original = Image.open(original_path).convert("RGBA")
    inpainted = Image.open(io.BytesIO(inpainted_bytes)).convert("RGBA")
    if inpainted.size != original.size:
        inpainted = inpainted.resize(original.size)

    mask = Image.new("L", original.size, 0)
    draw = ImageDraw.Draw(mask)
    left, top = max(mask_rect.left(), 0), max(mask_rect.top(), 0)
    right = min(mask_rect.left() + mask_rect.width(), original.width)
    bottom = min(mask_rect.top() + mask_rect.height(), original.height)
    draw.rectangle([left, top, right, bottom], fill=255)

    feather_px = min(FEATHER_MAX_PX, max(FEATHER_MIN_PX, int(min(mask_rect.width(), mask_rect.height()) * FEATHER_FRACTION)))
    mask = mask.filter(ImageFilter.GaussianBlur(radius=feather_px))

    blended = Image.composite(inpainted, original, mask).convert("RGB")

    save_kwargs = {"quality": 95} if output_path.suffix.lower() in (".jpg", ".jpeg", ".webp") else {}
    blended.save(output_path, **save_kwargs)


def _find_iopaint_executable() -> str:
    found = shutil.which("iopaint")
    if found:
        return found

    # Cuando la app corre como .exe empaquetado (PyInstaller), sys.executable apunta al
    # propio .exe, no a un intérprete de Python — así que ese candidato casi nunca existe
    # en ese escenario. Se buscan además las ubicaciones típicas donde `pip install iopaint`
    # deja el ejecutable en Windows, para no depender de que el usuario edite su PATH.
    candidates = [Path(sys.executable).parent / "Scripts" / "iopaint.exe"]

    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        candidates.extend(Path(local_appdata, "Programs", "Python").glob("Python*/Scripts/iopaint.exe"))

    appdata = os.environ.get("APPDATA")
    if appdata:
        candidates.extend(Path(appdata, "Python").glob("Python*/Scripts/iopaint.exe"))

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    raise InpaintingEngineError(
        "No se encontró el ejecutable de IOPaint. Instálalo con: pip install iopaint"
    )


class IOPaintEngine(InpaintingEngine):
    """Motor de inpainting basado en IOPaint.

    Usa un servidor IOPaint persistente en segundo plano (ver `core/iopaint_server.py`)
    para evitar el costo fijo de arrancar un proceso Python + importar PyTorch en cada
    imagen (~15s medidos, sin importar el modelo). Si el servidor no puede arrancar por
    algún motivo, cae de vuelta al modo CLI (un proceso por imagen, más lento pero sin
    dependencias adicionales) para no dejar la función totalmente rota.
    """

    def __init__(self, model: str = "migan", device: str = "cpu"):
        self.model = model
        self.device = device
        self._server = None  # se crea de forma perezosa para no importar iopaint_server sin necesidad

    def _get_server(self):
        if self._server is None:
            from watermark_remover.core.iopaint_server import IOPaintServer

            self._server = IOPaintServer(model=self.model, device=self.device)
        return self._server

    def shutdown(self):
        """Detiene el servidor en segundo plano, si está corriendo. Llamar al cerrar la app."""
        if self._server is not None:
            self._server.shutdown()

    def process(self, image_path: Path, mask_rect: QRect, output_path: Path) -> Path:
        if not image_path.exists():
            raise InpaintingEngineError(f"Imagen no encontrada: {image_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            inpainted_bytes = self._process_via_server(image_path, mask_rect)
        except InpaintingEngineError:
            inpainted_bytes = self._process_via_cli(image_path, mask_rect)

        try:
            _feather_blend(image_path, inpainted_bytes, mask_rect, output_path)
        except Exception as exc:  # noqa: BLE001 - no debe tumbar el flujo por el post-proceso
            raise InpaintingEngineError(f"No se pudo combinar el resultado: {exc}") from exc

        return output_path

    def _process_via_server(self, image_path: Path, mask_rect: QRect) -> bytes:
        server = self._get_server()
        server.ensure_running()

        image_b64 = _bytes_to_b64(image_path.read_bytes())
        mask_b64 = _bytes_to_b64(_qimage_to_bytes(_rect_to_mask_image(mask_rect, image_path)))

        try:
            resp = requests.post(
                f"{server.base_url}/api/v1/inpaint",
                json={"image": image_b64, "mask": mask_b64},
                timeout=SERVER_REQUEST_TIMEOUT_SECONDS,
            )
        except requests.exceptions.RequestException as exc:
            raise InpaintingEngineError(f"El servidor de IOPaint no respondió: {exc}") from exc

        if resp.status_code != 200:
            raise InpaintingEngineError(f"El servidor de IOPaint devolvió error {resp.status_code}: {resp.text[:300]}")

        return resp.content

    def _process_via_cli(self, image_path: Path, mask_rect: QRect) -> bytes:
        """Respaldo: un proceso de IOPaint por imagen (más lento, ver docstring de la clase)."""
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

            # IOPaint no siempre conserva la extensión original (ej. una entrada .webp
            # puede salir como .png) — se busca por nombre base, sin asumir la extensión.
            produced_candidates = sorted(output_dir.glob(f"{image_path.stem}.*"))
            if not produced_candidates:
                raise InpaintingEngineError("IOPaint no generó el archivo de salida esperado.")

            return produced_candidates[0].read_bytes()


def _bytes_to_b64(data: bytes) -> str:
    import base64

    return base64.b64encode(data).decode()
