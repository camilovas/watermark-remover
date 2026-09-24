from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

from watermark_remover.core.inpainting_engine import InpaintingEngine, InpaintingEngineError


class _CallableSignals(QObject):
    finished = Signal(object)
    error = Signal(str)


class _CallableTask(QRunnable):
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = _CallableSignals()

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception as exc:  # noqa: BLE001 - reportar cualquier fallo a la UI, no crashear
            self.signals.error.emit(str(exc))


# Mantiene referencias vivas mientras las tareas corren en el QThreadPool: sin esto,
# Python puede recolectar la tarea (y su QObject de señales) antes de que run() termine,
# y el callback de finished/error nunca se dispara.
_active_tasks: set[_CallableTask] = set()


def run_in_background(func, on_finished, on_error, *args, **kwargs):
    task = _CallableTask(func, *args, **kwargs)
    _active_tasks.add(task)

    def _cleanup_and_forward(handler, value):
        _active_tasks.discard(task)
        handler(value)

    task.signals.finished.connect(lambda result: _cleanup_and_forward(on_finished, result))
    task.signals.error.connect(lambda message: _cleanup_and_forward(on_error, message))
    QThreadPool.globalInstance().start(task)


def process_async(engine: InpaintingEngine, image_path: Path, mask_rect, output_path: Path, on_finished, on_error):
    def _run():
        return engine.process(image_path, mask_rect, output_path)

    def _on_finished(result_path):
        on_finished(result_path)

    def _on_error(message):
        on_error(message)

    run_in_background(_run, _on_finished, _on_error)
