from pathlib import Path

from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon
from PySide6.QtWidgets import QListWidget, QListWidgetItem

from watermark_remover.core.image_item import ImageItem
from watermark_remover.utils.image_utils import is_supported_format, make_thumbnail

THUMBNAIL_SIZE = 96


class ImageListWidget(QListWidget):
    images_added = Signal(list)  # list[ImageItem]
    unsupported_files = Signal(list)  # list[str] rutas rechazadas
    current_item_changed = Signal(object)  # ImageItem | None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIconSize(QSize(THUMBNAIL_SIZE, THUMBNAIL_SIZE))
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDropMode.NoDragDrop)
        self.currentItemChanged.connect(self._on_current_item_changed)

    def add_paths(self, paths: list[str]):
        accepted: list[ImageItem] = []
        rejected: list[str] = []

        for raw_path in paths:
            path = Path(raw_path)
            if not is_supported_format(path):
                rejected.append(raw_path)
                continue
            try:
                thumbnail = make_thumbnail(path, THUMBNAIL_SIZE)
            except ValueError:
                rejected.append(raw_path)
                continue

            item = ImageItem(path=path)
            list_item = QListWidgetItem(QIcon(thumbnail), path.name)
            list_item.setData(1000, item)
            self.addItem(list_item)
            accepted.append(item)

        if accepted:
            self.images_added.emit(accepted)
        if rejected:
            self.unsupported_files.emit(rejected)

    def current_image_item(self) -> ImageItem | None:
        item = self.currentItem()
        return item.data(1000) if item else None

    def _on_current_item_changed(self, current: QListWidgetItem, _previous: QListWidgetItem):
        self.current_item_changed.emit(current.data(1000) if current else None)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            paths = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]
            self.add_paths(paths)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)
