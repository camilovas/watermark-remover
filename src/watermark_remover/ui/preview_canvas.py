from pathlib import Path

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QMouseEvent, QPixmap
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView

from watermark_remover.ui.mask_editor import MaskRectItem


class PreviewCanvas(QGraphicsView):
    mask_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHint(self.renderHints())
        self.setDragMode(QGraphicsView.DragMode.NoDrag)

        self._pixmap_item: QGraphicsPixmapItem | None = None
        self._mask_item: MaskRectItem | None = None
        self._drawing_new_mask = False
        self._draw_start = None

    def load_image(self, path: Path):
        self._scene.clear()
        self._mask_item = None
        pixmap = QPixmap(str(path))
        self._pixmap_item = self._scene.addPixmap(pixmap)
        self._scene.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def clear_mask(self):
        if self._mask_item is not None:
            self._scene.removeItem(self._mask_item)
            self._mask_item = None
            self.mask_changed.emit()

    def has_mask(self) -> bool:
        return self._mask_item is not None

    def mask_rect(self) -> QRectF | None:
        if self._mask_item is None:
            return None
        return self._mask_item.scene_rect()

    def _set_mask_rect(self, rect: QRectF):
        if self._mask_item is not None:
            self._scene.removeItem(self._mask_item)
        self._mask_item = MaskRectItem(QRectF(0, 0, rect.width(), rect.height()))
        self._mask_item.setPos(rect.topLeft())
        self._scene.addItem(self._mask_item)
        self.mask_changed.emit()

    def mousePressEvent(self, event: QMouseEvent):
        if self._pixmap_item is None:
            return super().mousePressEvent(event)

        item_under_cursor = self.itemAt(event.pos())
        if item_under_cursor is self._mask_item or (
            self._mask_item is not None and item_under_cursor in self._mask_item.childItems()
        ):
            return super().mousePressEvent(event)

        # Clic sobre la imagen (fuera de la máscara existente): empezar a dibujar una nueva.
        self._drawing_new_mask = True
        self._draw_start = self.mapToScene(event.pos())
        self._set_mask_rect(QRectF(self._draw_start, self._draw_start))
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drawing_new_mask and self._mask_item is not None:
            current = self.mapToScene(event.pos())
            rect = QRectF(self._draw_start, current).normalized()
            self._mask_item.setPos(rect.topLeft())
            self._mask_item.setRect(0, 0, rect.width(), rect.height())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._drawing_new_mask:
            self._drawing_new_mask = False
            self.mask_changed.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)
