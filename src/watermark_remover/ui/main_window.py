import time
from pathlib import Path

from PySide6.QtCore import QRectF, Qt, QTimer
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

from watermark_remover.core.batch_processor import BatchProcessor, BatchResult
from watermark_remover.core.image_item import ImageItem, ImageStatus
from watermark_remover.core.inpainting_engine import IOPaintEngine
from watermark_remover.core.watermark_detector import create_detector
from watermark_remover.ui.image_list_widget import ImageListWidget
from watermark_remover.ui.preview_canvas import PreviewCanvas
from watermark_remover.ui.processing_worker import process_async, run_in_background
from watermark_remover.ui.progress_dialog import ProgressDialog
from watermark_remover.utils.file_utils import safe_output_path
from watermark_remover.utils.image_utils import SUPPORTED_EXTENSIONS


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quitar Marca de Agua")
        self.resize(1100, 700)

        self.engine = IOPaintEngine()
        self._showing_result = False
        self._detector = None  # se resuelve de forma perezosa (create_detector hace una llamada de red)
        self._batch_thread: BatchProcessor | None = None
        self._progress_dialog: ProgressDialog | None = None

        # IOPaint/Ollama no reportan un % real de avance por imagen (son una sola llamada
        # bloqueante), así que en vez de fingir un porcentaje se muestra el tiempo
        # transcurrido en vivo — responde igual a "cuánto se está demorando".
        self._elapsed_timer = QTimer(self)
        self._elapsed_timer.setInterval(1000)
        self._elapsed_timer.timeout.connect(self._tick_elapsed_timer)
        self._elapsed_start: float = 0.0
        self._elapsed_label_base: str = ""

        self.image_list = ImageListWidget()
        self.image_list.images_added.connect(self._on_images_added)
        self.image_list.unsupported_files.connect(self._on_unsupported_files)
        self.image_list.current_item_changed.connect(self._on_current_item_changed)

        self.canvas = PreviewCanvas()
        self.canvas.mask_changed.connect(self._on_mask_changed)

        self.add_button = QPushButton("Agregar imágenes")
        self.add_button.clicked.connect(self._open_file_dialog)

        self.detect_button = QPushButton("Detectar automáticamente")
        self.detect_button.clicked.connect(self._detect_current)
        self.detect_button.setEnabled(False)

        self.clear_mask_button = QPushButton("Limpiar máscara")
        self.clear_mask_button.clicked.connect(self.canvas.clear_mask)
        self.clear_mask_button.setEnabled(False)

        self.process_button = QPushButton("Procesar")
        self.process_button.clicked.connect(self._process_current)
        self.process_button.setEnabled(False)

        self.process_all_button = QPushButton("Procesar todas (lote)")
        self.process_all_button.clicked.connect(self._process_batch)
        self.process_all_button.setEnabled(False)

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
        left_panel.addWidget(self.process_all_button)
        left_widget = QWidget()
        left_widget.setLayout(left_panel)

        right_panel = QVBoxLayout()
        right_panel.addWidget(self.canvas)
        button_row = QHBoxLayout()
        button_row.addWidget(self.detect_button)
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
        self._refresh_ollama_availability()

    # --- Contador de tiempo transcurrido (IOPaint/Ollama no reportan % real) ------

    def _start_elapsed_timer(self, base_message: str):
        self._elapsed_label_base = base_message
        self._elapsed_start = time.monotonic()
        self.status_label.setText(f"{base_message} (0s)")
        self._elapsed_timer.start()

    def _stop_elapsed_timer(self):
        self._elapsed_timer.stop()

    def _tick_elapsed_timer(self):
        elapsed = int(time.monotonic() - self._elapsed_start)
        self.status_label.setText(f"{self._elapsed_label_base} ({elapsed}s)")

    # --- Ollama (detección automática, opcional) --------------------------

    def _refresh_ollama_availability(self):
        def _resolve():
            return create_detector()

        run_in_background(_resolve, self._on_detector_resolved, self._on_detector_resolve_error)

    def _on_detector_resolved(self, detector):
        self._detector = detector
        # NullDetector no tiene is_available(); solo el real la expone.
        available = hasattr(detector, "is_available")
        self.detect_button.setVisible(available)
        if available:
            self.detect_button.setEnabled(self.image_list.current_image_item() is not None)

    def _on_detector_resolve_error(self, _message: str):
        self.detect_button.setVisible(False)

    def _detect_current(self):
        item = self.image_list.current_image_item()
        if item is None or self._detector is None:
            return

        self.detect_button.setEnabled(False)
        self._start_elapsed_timer("Detectando región de la marca de agua con Ollama...")

        run_in_background(
            self._detector.detect,
            lambda rect, item=item: self._on_detect_finished(item, rect),
            lambda message, item=item: self._on_detect_error(item, message),
            item.path,
        )

    def _on_detect_finished(self, item: ImageItem, rect):
        self._stop_elapsed_timer()
        self.detect_button.setEnabled(True)
        if self.image_list.current_image_item() is not item:
            return  # el usuario cambió de imagen mientras se detectaba
        if rect is None:
            self.status_label.setText(
                "Ollama no encontró una marca de agua clara — es un modelo pequeño y puede fallar en marcas "
                "sutiles/semitransparentes. Marca la región manualmente."
            )
            return
        self.canvas._set_mask_rect(QRectF(rect))
        self.status_label.setText(
            "Región sugerida por Ollama — revísala con cuidado antes de procesar, puede no ser exacta."
        )

    def _on_detect_error(self, item: ImageItem, message: str):
        self._stop_elapsed_timer()
        self.detect_button.setEnabled(True)
        self.status_label.setText("No se pudo detectar automáticamente. Marca la región manualmente.")

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
        self.process_all_button.setEnabled(self.image_list.count() > 0)

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
            self.detect_button.setEnabled(False)
            return
        self.canvas.load_image(item.path)
        self.process_button.setEnabled(False)
        self.clear_mask_button.setEnabled(False)
        if self._detector is not None and hasattr(self._detector, "is_available"):
            self.detect_button.setEnabled(True)
        if item.result_path and item.result_path.exists():
            self.compare_button.setEnabled(True)
            self.save_button.setEnabled(True)

    # --- Máscara -------------------------------------------------------

    def _on_mask_changed(self):
        has_mask = self.canvas.has_mask()
        self.clear_mask_button.setEnabled(has_mask)
        self.process_button.setEnabled(has_mask)

    # --- Procesamiento individual -----------------------------------------

    def _process_current(self):
        item = self.image_list.current_image_item()
        mask_rect = self.canvas.mask_rect()
        if item is None or mask_rect is None:
            return

        item.status = ImageStatus.PROCESSING
        self._set_busy(True)
        self._start_elapsed_timer(f"Procesando {item.name}...")

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
        self._stop_elapsed_timer()
        elapsed = int(time.monotonic() - self._elapsed_start)
        item.status = ImageStatus.DONE
        item.result_path = result_path
        self._set_busy(False)
        self.status_label.setText(f"Listo: {item.name} procesada en {elapsed}s.")
        self.compare_button.setEnabled(True)
        self.save_button.setEnabled(True)

    def _on_process_error(self, item: ImageItem, message: str):
        self._stop_elapsed_timer()
        item.status = ImageStatus.ERROR
        item.error_message = message
        self._set_busy(False)
        self.status_label.setText("Error al procesar la imagen.")
        QMessageBox.critical(self, "Error de procesamiento", message)

    def _set_busy(self, busy: bool):
        self.progress_bar.setVisible(busy)
        self.process_button.setEnabled(not busy and self.canvas.has_mask())
        self.add_button.setEnabled(not busy)

    # --- Procesamiento por lotes --------------------------------------------

    def _process_batch(self):
        items = [self.image_list.item(i).data(1000) for i in range(self.image_list.count())]
        if not items:
            return

        default_mask = self.canvas.mask_rect()
        if default_mask is None and not any(item.mask_rect for item in items):
            QMessageBox.information(
                self, "Falta una máscara",
                "Marca la región de la marca de agua en al menos la imagen actual antes de procesar el lote "
                "(esa máscara se usará como referencia para las imágenes que no tengan una propia).",
            )
            return

        default_qrect = default_mask.toRect() if default_mask is not None else None

        self.add_button.setEnabled(False)
        self.process_all_button.setEnabled(False)
        self.process_button.setEnabled(False)

        self._progress_dialog = ProgressDialog(total=len(items), parent=self)
        self._progress_dialog.cancel_requested.connect(self._cancel_batch)

        self._batch_thread = BatchProcessor(self.engine, items, default_qrect)
        self._batch_thread.item_started.connect(self._progress_dialog.set_progress)
        self._batch_thread.batch_finished.connect(self._on_batch_finished)
        self._batch_thread.start()

        self._progress_dialog.exec()

    def _cancel_batch(self):
        if self._batch_thread is not None:
            self._batch_thread.cancel()

    def _on_batch_finished(self, results: list[BatchResult]):
        if self._progress_dialog is not None:
            self._progress_dialog.accept()
            self._progress_dialog = None

        self.add_button.setEnabled(True)
        self.process_all_button.setEnabled(True)
        self.process_button.setEnabled(self.canvas.has_mask())

        successes = sum(1 for r in results if r.success)
        failures = [r for r in results if not r.success]
        summary = f"Lote terminado: {successes}/{len(results)} imágenes procesadas correctamente."
        self.status_label.setText(summary)

        if failures:
            details = "\n".join(f"- {r.item.name}: {r.error_message}" for r in failures)
            QMessageBox.warning(self, "Algunas imágenes fallaron", f"{summary}\n\n{details}")

        current = self.image_list.current_image_item()
        if current is not None and current.result_path and current.result_path.exists():
            self.compare_button.setEnabled(True)
            self.save_button.setEnabled(True)

        self._batch_thread = None

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

    # --- Cierre de la app -------------------------------------------------

    def closeEvent(self, event):
        # Evita dejar el servidor de IOPaint en segundo plano corriendo huérfano.
        self.engine.shutdown()
        super().closeEvent(event)
