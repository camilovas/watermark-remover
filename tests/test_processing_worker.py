import sys
import time
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from PySide6.QtCore import QRect
from PySide6.QtWidgets import QApplication

from watermark_remover.ui.processing_worker import process_async


@pytest.fixture(scope="module", autouse=True)
def qapp():
    return QApplication.instance() or QApplication([])


def _spin_until(predicate, timeout=5.0):
    app = QApplication.instance()
    start = time.time()
    while not predicate() and time.time() - start < timeout:
        app.processEvents()
        time.sleep(0.01)


def test_process_async_survives_gc_and_calls_on_finished(tmp_path):
    """Regresión: el QRunnable no debe perderse por garbage collection antes de emitir su señal."""
    engine = MagicMock()
    engine.process.return_value = tmp_path / "resultado.png"

    result = {}
    process_async(
        engine,
        tmp_path / "img.png",
        QRect(0, 0, 10, 10),
        tmp_path / "resultado.png",
        on_finished=lambda p: result.update(path=p),
        on_error=lambda m: result.update(error=m),
    )

    # Forzar un ciclo de garbage collection explícito para simular el escenario del bug.
    import gc
    gc.collect()

    _spin_until(lambda: bool(result))

    assert result == {"path": tmp_path / "resultado.png"}


def test_process_async_reports_error(tmp_path):
    engine = MagicMock()
    engine.process.side_effect = RuntimeError("motor no disponible")

    result = {}
    process_async(
        engine,
        tmp_path / "img.png",
        QRect(0, 0, 10, 10),
        tmp_path / "resultado.png",
        on_finished=lambda p: result.update(path=p),
        on_error=lambda m: result.update(error=m),
    )

    _spin_until(lambda: bool(result))

    assert "error" in result
