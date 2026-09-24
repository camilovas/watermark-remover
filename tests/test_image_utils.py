import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from watermark_remover.utils.image_utils import is_supported_format, make_thumbnail

FIXTURE = Path(__file__).parent / "fixtures" / "sample_watermarked.png"


def test_supported_formats():
    assert is_supported_format("foto.png")
    assert is_supported_format("foto.JPG")
    assert is_supported_format("foto.jpeg")
    assert is_supported_format("foto.webp")


def test_unsupported_formats():
    assert not is_supported_format("documento.pdf")
    assert not is_supported_format("video.mp4")
    assert not is_supported_format("sin_extension")


def test_make_thumbnail_returns_scaled_pixmap():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    thumb = make_thumbnail(FIXTURE, max_size=64)
    assert thumb.width() <= 64
    assert thumb.height() <= 64


def test_make_thumbnail_invalid_image_raises():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    import pytest

    with pytest.raises(ValueError):
        make_thumbnail(Path(__file__), max_size=64)
