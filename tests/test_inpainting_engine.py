import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from PySide6.QtCore import QRect
from PySide6.QtWidgets import QApplication

from watermark_remover.core.inpainting_engine import (
    IOPaintEngine,
    InpaintingEngineError,
    _rect_to_mask_image,
)

FIXTURE = Path(__file__).parent / "fixtures" / "sample_watermarked.png"


@pytest.fixture(scope="module", autouse=True)
def qapp():
    return QApplication.instance() or QApplication([])


def test_rect_to_mask_image_white_region_matches_rect():
    mask_rect = QRect(850, 700, 330, 80)
    mask = _rect_to_mask_image(mask_rect, FIXTURE)

    assert mask.pixelColor(900, 720).red() == 255  # dentro del rectángulo
    assert mask.pixelColor(10, 10).red() == 0  # fuera del rectángulo


def test_rect_to_mask_image_missing_source_raises():
    with pytest.raises(InpaintingEngineError):
        _rect_to_mask_image(QRect(0, 0, 10, 10), Path("no_existe.png"))


@patch("watermark_remover.core.inpainting_engine.subprocess.run")
@patch("watermark_remover.core.inpainting_engine._find_iopaint_executable", return_value="iopaint")
def test_ioaint_engine_calls_cli_with_expected_args(mock_find, mock_run, tmp_path):
    output_dir_holder = {}

    def fake_run(cmd, **kwargs):
        # el motor crea un archivo con el mismo nombre de la imagen dentro de --output
        out_idx = cmd.index("--output") + 1
        out_dir = Path(cmd[out_idx])
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / FIXTURE.name).write_bytes(b"resultado-fake")
        return MagicMock(returncode=0, stdout="", stderr="")

    mock_run.side_effect = fake_run

    engine = IOPaintEngine()
    output_path = tmp_path / "resultado.png"
    result = engine.process(FIXTURE, QRect(850, 700, 330, 80), output_path)

    assert result == output_path
    assert output_path.exists()

    called_cmd = mock_run.call_args.args[0]
    assert "--model" in called_cmd and "lama" in called_cmd
    assert "--device" in called_cmd and "cpu" in called_cmd


@patch("watermark_remover.core.inpainting_engine.subprocess.run")
@patch("watermark_remover.core.inpainting_engine._find_iopaint_executable", return_value="iopaint")
def test_ioaint_engine_raises_on_nonzero_exit(mock_find, mock_run, tmp_path):
    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="modelo no disponible")

    engine = IOPaintEngine()
    with pytest.raises(InpaintingEngineError):
        engine.process(FIXTURE, QRect(0, 0, 10, 10), tmp_path / "out.png")


def test_ioaint_engine_missing_image_raises(tmp_path):
    engine = IOPaintEngine()
    with pytest.raises(InpaintingEngineError):
        engine.process(Path("no_existe.png"), QRect(0, 0, 10, 10), tmp_path / "out.png")
