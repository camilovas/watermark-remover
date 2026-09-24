from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

from watermark_remover.core.inpainting_engine import InpaintingEngine, InpaintingEngineError


class _WorkerSignals(QObject):
    finished = Signal(Path)  # output_path
    error = Signal(str)


class _ProcessTask(QRunnable):
    def __init__(self, engine: InpaintingEngine, image_path: Path, mask_rect, output_path: Path):
        super().__init__()
        self.engine = engine
        self.image_path = image_path
        self.mask_rect = mask_rect
        self.output_path = output_path
        self.signals = _WorkerSignals()

    def run(self):
        try:
            result = self.engine.process(self.image_path, self.mask_rect, self.output_path)
            self.signals.finished.emit(result)
        except InpaintingEngineError as exc:
            self.signals.error.emit(str(exc))
        except Exception as exc:  # noqa: BLE001 - reportar cualquier fallo inesperado a la UI, no crashear
            self.signals.error.emit(f"Error inesperado: {exc}")


_active_tasks: set[_ProcessTask] = set()


def process_async(engine: InpaintingEngine, image_path: Path, mask_rect, output_path: Path, on_finished, on_error):
    task = _ProcessTask(engine, image_path, mask_rect, output_path)
    # Mantiene una referencia viva mientras corre en el QThreadPool: sin esto, Python
    # puede recolectar `task` (y su QObject de señales) antes de que run() termine.
    _active_tasks.add(task)

    def _cleanup_and_forward(handler, *args):
        _active_tasks.discard(task)
        handler(*args)

    task.signals.finished.connect(lambda result: _cleanup_and_forward(on_finished, result))
    task.signals.error.connect(lambda message: _cleanup_and_forward(on_error, message))
    QThreadPool.globalInstance().start(task)
