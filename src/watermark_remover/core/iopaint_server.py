import socket
import subprocess
import threading
import time

import requests

from watermark_remover.core.inpainting_engine import InpaintingEngineError, _find_iopaint_executable

SERVER_STARTUP_TIMEOUT_SECONDS = 60
SERVER_POLL_INTERVAL_SECONDS = 0.5


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class IOPaintServer:
    """Mantiene un servidor de IOPaint corriendo en segundo plano para evitar el costo
    de arrancar un proceso Python + importar PyTorch desde cero en cada imagen
    (~15s de overhead fijo por llamada, medido en el spike de rendimiento — ver
    docs/research/best_practices.md). Con el servidor persistente, cada imagen
    solo paga el costo de la inferencia real (unos pocos segundos con migan)."""

    def __init__(self, model: str = "migan", device: str = "cpu"):
        self.model = model
        self.device = device
        self.host = "127.0.0.1"
        self.port: int | None = None
        self._process: subprocess.Popen | None = None
        self._lock = threading.Lock()

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def _is_up(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/api/v1/server-config", timeout=2)
            return resp.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def ensure_running(self):
        """Arranca el servidor si no está corriendo. Seguro de llamar repetidamente."""
        with self._lock:
            if self._process is not None and self._process.poll() is None and self._is_up():
                return  # ya está corriendo

            executable = _find_iopaint_executable()
            self.port = _find_free_port()

            self._process = subprocess.Popen(
                [
                    executable, "start",
                    "--model", self.model,
                    "--device", self.device,
                    "--host", self.host,
                    "--port", str(self.port),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )

            deadline = time.monotonic() + SERVER_STARTUP_TIMEOUT_SECONDS
            while time.monotonic() < deadline:
                if self._process.poll() is not None:
                    raise InpaintingEngineError(
                        "El servidor de IOPaint terminó inesperadamente al arrancar."
                    )
                if self._is_up():
                    return
                time.sleep(SERVER_POLL_INTERVAL_SECONDS)

            raise InpaintingEngineError(
                f"El servidor de IOPaint no respondió tras {SERVER_STARTUP_TIMEOUT_SECONDS}s."
            )

    def shutdown(self):
        with self._lock:
            if self._process is not None and self._process.poll() is None:
                self._process.terminate()
                try:
                    self._process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self._process.kill()
            self._process = None
