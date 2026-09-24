from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QObject, QRect, QThread, Signal

from watermark_remover.core.image_item import ImageItem, ImageStatus
from watermark_remover.core.inpainting_engine import InpaintingEngine, InpaintingEngineError
from watermark_remover.utils.file_utils import safe_output_path


@dataclass
class BatchResult:
    item: ImageItem
    success: bool
    error_message: str | None = None


class BatchProcessor(QThread):
    """Procesa una lista de ImageItem con el mismo InpaintingEngine, en un hilo separado.

    Emite progreso por imagen y continúa aunque una imagen individual falle.
    Cancelación cooperativa: se chequea entre imágenes, nunca a mitad de una ya en curso
    (no corrompe archivos ya guardados).
    """

    item_started = Signal(int, int, str)  # índice (1-based), total, nombre
    item_finished = Signal(BatchResult)
    batch_finished = Signal(list)  # list[BatchResult]

    def __init__(self, engine: InpaintingEngine, items: list[ImageItem], default_mask_rect: QRect, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.items = items
        self.default_mask_rect = default_mask_rect
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        results: list[BatchResult] = []
        total = len(self.items)

        for index, item in enumerate(self.items, start=1):
            if self._cancelled:
                break

            self.item_started.emit(index, total, item.name)
            item.status = ImageStatus.PROCESSING
            mask_rect = item.mask_rect if item.mask_rect is not None else self.default_mask_rect

            try:
                output_path = safe_output_path(item.path)
                result_path = self.engine.process(item.path, mask_rect, output_path)
                item.status = ImageStatus.DONE
                item.result_path = result_path
                result = BatchResult(item=item, success=True)
            except InpaintingEngineError as exc:
                item.status = ImageStatus.ERROR
                item.error_message = str(exc)
                result = BatchResult(item=item, success=False, error_message=str(exc))
            except Exception as exc:  # noqa: BLE001 - no debe tumbar el hilo del lote
                item.status = ImageStatus.ERROR
                item.error_message = f"Error inesperado: {exc}"
                result = BatchResult(item=item, success=False, error_message=item.error_message)

            results.append(result)
            self.item_finished.emit(result)

        self.batch_finished.emit(results)
