from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QLabel, QProgressBar, QPushButton, QVBoxLayout


class ProgressDialog(QDialog):
    cancel_requested = Signal()

    def __init__(self, total: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Procesando lote")
        self.setModal(True)
        self.setMinimumWidth(360)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(0)

        self.label = QLabel(f"0 de {total} imágenes procesadas...")

        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self._on_cancel_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

    def set_progress(self, current: int, total: int, name: str):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.label.setText(f"Procesando {current} de {total}: {name}")

    def _on_cancel_clicked(self):
        self.cancel_button.setEnabled(False)
        self.label.setText(self.label.text() + " (cancelando...)")
        self.cancel_requested.emit()
