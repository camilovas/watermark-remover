from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsSceneMouseEvent

HANDLE_SIZE = 10
_HANDLES = ["top_left", "top_right", "bottom_left", "bottom_right"]


class MaskRectItem(QGraphicsRectItem):
    """Rectángulo de máscara: se puede mover (arrastrar el centro) y redimensionar (arrastrar esquinas)."""

    def __init__(self, rect: QRectF):
        super().__init__(rect)
        self.setPen(QPen(QColor(255, 60, 60), 2, Qt.PenStyle.DashLine))
        self.setBrush(QBrush(QColor(255, 60, 60, 60)))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)
        self._active_handle: str | None = None
        self._drag_start_rect = QRectF()
        self._drag_start_pos = QPointF()

    def _handle_at(self, pos: QPointF) -> str | None:
        r = self.rect()
        corners = {
            "top_left": r.topLeft(),
            "top_right": r.topRight(),
            "bottom_left": r.bottomLeft(),
            "bottom_right": r.bottomRight(),
        }
        for name, corner in corners.items():
            if (pos - corner).manhattanLength() <= HANDLE_SIZE:
                return name
        return None

    def hoverMoveEvent(self, event):
        handle = self._handle_at(event.pos())
        if handle in ("top_left", "bottom_right"):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif handle in ("top_right", "bottom_left"):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        self._active_handle = self._handle_at(event.pos())
        self._drag_start_rect = QRectF(self.rect())
        self._drag_start_pos = event.pos()
        if self._active_handle:
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        if self._active_handle:
            delta = event.pos() - self._drag_start_pos
            r = QRectF(self._drag_start_rect)
            if self._active_handle == "top_left":
                r.setTopLeft(r.topLeft() + delta)
            elif self._active_handle == "top_right":
                r.setTopRight(r.topRight() + delta)
            elif self._active_handle == "bottom_left":
                r.setBottomLeft(r.bottomLeft() + delta)
            elif self._active_handle == "bottom_right":
                r.setBottomRight(r.bottomRight() + delta)
            self.setRect(r.normalized())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        self._active_handle = None
        super().mouseReleaseEvent(event)

    def scene_rect(self) -> QRectF:
        """Devuelve el rectángulo de la máscara en coordenadas de la escena (imagen)."""
        return self.mapRectToScene(self.rect())
