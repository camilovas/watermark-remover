import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest
from PySide6.QtWidgets import QApplication

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session", autouse=True)
def qapp():
    """QApplication única para toda la sesión de tests — PySide6 exige una sola instancia."""
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def sample_image_path() -> Path:
    return FIXTURES_DIR / "sample_watermarked.png"
