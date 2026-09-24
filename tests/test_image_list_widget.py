import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from PySide6.QtWidgets import QApplication

from watermark_remover.ui.image_list_widget import ImageListWidget

FIXTURE = Path(__file__).parent / "fixtures" / "sample_watermarked.png"


@pytest.fixture(scope="module", autouse=True)
def qapp():
    return QApplication.instance() or QApplication([])


def test_add_supported_image_adds_item():
    widget = ImageListWidget()
    received = []
    widget.images_added.connect(lambda items: received.append(items))

    widget.add_paths([str(FIXTURE)])

    assert widget.count() == 1
    assert len(received) == 1 and len(received[0]) == 1
    assert received[0][0].path == FIXTURE


def test_add_unsupported_format_is_rejected(tmp_path):
    fake_pdf = tmp_path / "documento.pdf"
    fake_pdf.write_bytes(b"fake")

    widget = ImageListWidget()
    rejected = []
    widget.unsupported_files.connect(lambda paths: rejected.append(paths))

    widget.add_paths([str(fake_pdf)])

    assert widget.count() == 0
    assert rejected == [[str(fake_pdf)]]


def test_current_image_item_tracks_selection():
    widget = ImageListWidget()
    widget.add_paths([str(FIXTURE)])
    widget.setCurrentRow(0)

    current = widget.current_image_item()
    assert current is not None
    assert current.path == FIXTURE


def test_current_image_item_none_when_empty():
    widget = ImageListWidget()
    assert widget.current_image_item() is None
