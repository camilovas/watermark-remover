from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from watermark_remover.core.image_item import ImageItem, ImageStatus
from watermark_remover.core.inpainting_engine import IOPaintEngine
from watermark_remover.ui.image_list_widget import ImageListWidget
from watermark_remover.ui.preview_canvas import PreviewCanvas
from watermark_remover.ui.processing_worker import process_async
from watermark_remover.utils.file_utils import safe_output_path
from watermark_remover.utils.image_utils import SUPPORTED_EXTENSIONS


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quitar Marca de Agua")
        self.resize(1100, 700)

        self.engine = IOPaintEngine()
        self._showing_result = False

        self.image_list = ImageListWidget()
        self.image_list.images_added.connect(self._on_images_added)
        self.image_list.unsupported_files.connect(self._on_unsupported_files)
        self.image_list.current_item_changed.connect(self._on_current_item_changed)

        self.canvas = PreviewCanvas()
        self.canvas.mask_changed.connect(self._on_mask_changed)

        self.add_button = QPushButton("Agregar imágenes")
        self.add_button.clicked.connect(self._open_file_dialog)

        self.clear_mask_button = QPushButton("Limpiar máscara")
        self.clear_mask_button.clicked.connect(self.canvas.clear_mask)
        self.clear_mask_button.setEnabled(False)

        self.process_button = QPushButton("Procesar")
        self.process_button.clicked.connect(self._process_current)
        self.process_button.setEnabled(False)

        self.compare_button = QPushButton("Ver antes/después")
        self.compare_button.clicked.connect(self._toggle_before_after)
        self.compare_button.setEnabled(False)

        self.save_button = QPushButton("Guardar resultado")
        self.save_button.clicked.connect(self._save_result)
        self.save_button.setEnabled(False)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # indeterminado
        self.progress_bar.setVisible(False)

        self.status_label = QLabel("Agrega imágenes para comenzar.")

        left_panel = QVBoxLayout()
        left_panel.addWidget(self.add_button)
        left_panel.addWidget(self.image_list)
        left_widget = QWidget()
        left_widget.setLayout(left_panel)

        right_panel = QVBoxLayout()
        right_panel.addWidget(self.canvas)
        button_row = QHBoxLayout()
        button_row.addWidget(self.clear_mask_button)
        button_row.addWidget(self.process_button)
        button_row.addWidget(self.compare_button)
        button_row.addWidget(self.save_button)
        right_panel.addLayout(button_row)
        right_panel.addWidget(self.progress_bar)
        right_panel.addWidget(self.status_label)
        right_widget = QWidget()
        right_widget.setLayout(right_panel)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)

        self.setAcceptDrops(True)

    # --- Carga de imágenes -------------------------------------------------

    def _open_file_dialog(self):
        patterns = " ".join(f"*{ext}" for ext in sorted(SUPPORTED_EXTENSIONS))
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Selecciona imágenes", "", f"Imágenes ({patterns})"
        )
        if paths:
            self.image_list.add_paths(paths)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            paths = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]
            self.image_list.add_paths(paths)
            event.acceptProposedAction()

    def _on_images_added(self, items: list[ImageItem]):
        self.status_label.setText(f"{self.image_list.count()} imagen(es) cargada(s).")
        if self.image_list.currentItem() is None and self.image_list.count() > 0:
            self.image_list.setCurrentRow(0)

    def _on_unsupported_files(self, paths: list[str]):
        names = "\n".join(Path(p).name for p in paths)
        QMessageBox.warning(
            self, "Formato no soportado",
            f"Estos archivos no se pudieron cargar (formato no soportado o imagen inválida):\n{names}",
        )

    def _on_current_item_changed(self, item: ImageItem | None):
        self._showing_result = False
        self.compare_button.setEnabled(False)
        self.save_button.setEnabled(False)
        if item is None:
            self.process_button.setEnabled(False)
            self.clear_mask_button.setEnabled(False)
            return
        self.canvas.load_image(item.path)
        self.process_button.setEnabled(False)
        self.clear_mask_button.setEnabled(False)
        if item.result_path and item.result_path.exists():
            self.compare_button.setEnabled(True)
            self.save_button.setEnabled(True)

    # --- Máscara -------------------------------------------------------

    def _on_mask_changed(self):
        has_mask = self.canvas.has_mask()
        self.clear_mask_button.setEnabled(has_mask)
        self.process_button.setEnabled(has_mask)

    # --- Procesamiento ---------------------------------------------------

    def _process_current(self):
        item = self.image_list.current_image_item()
        mask_rect = self.canvas.mask_rect()
        if item is None or mask_rect is None:
            return

        item.status = ImageStatus.PROCESSING
        self._set_busy(True, f"Procesando {item.name}...")

        output_path = safe_output_path(item.path)
        qrect = mask_rect.toRect()

        process_async(
            self.engine,
            item.path,
            qrect,
            output_path,
            on_finished=lambda result_path, item=item: self._on_process_finished(item, result_path),
            on_error=lambda message, item=item: self._on_process_error(item, message),
        )

    def _on_process_finished(self, item: ImageItem, result_path: Path):
        item.status = ImageStatus.DONE
        item.result_path = result_path
        self._set_busy(False, f"Listo: {item.name} procesada.")
        self.compare_button.setEnabled(True)
        self.save_button.setEnabled(True)

    def _on_process_error(self, item: ImageItem, message: str):
        item.status = ImageStatus.ERROR
        item.error_message = message
        self._set_busy(False, "Error al procesar la imagen.")
        QMessageBox.critical(self, "Error de procesamiento", message)

    def _set_busy(self, busy: bool, message: str):
        self.progress_bar.setVisible(busy)
        self.process_button.setEnabled(not busy and self.canvas.has_mask())
        self.add_button.setEnabled(not busy)
        self.status_label.setText(message)

    # --- Comparación / guardado ------------------------------------------

    def _toggle_before_after(self):
        item = self.image_list.current_image_item()
        if item is None or item.result_path is None:
            return
        self._showing_result = not self._showing_result
        path = item.result_path if self._showing_result else item.path
        self.canvas.load_image(path)
        self.compare_button.setText("Ver original" if self._showing_result else "Ver resultado")

    def _save_result(self):
        item = self.image_list.current_image_item()
        if item is None or item.result_path is None:
            return
        destination, _ = QFileDialog.getSaveFileName(
            self, "Guardar resultado", str(item.result_path), f"Imagen (*{item.path.suffix})"
        )
        if destination:
            QPixmap(str(item.result_path)).save(destination)
            self.status_label.setText(f"Guardado en {destination}")
