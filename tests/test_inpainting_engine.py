from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtCore import QRect

from watermark_remover.core.inpainting_engine import (
    IOPaintEngine,
    InpaintingEngineError,
    _find_iopaint_executable,
    _rect_to_mask_image,
)

FIXTURE = Path(__file__).parent / "fixtures" / "sample_watermarked.png"


def test_rect_to_mask_image_white_region_matches_rect():
    mask_rect = QRect(850, 700, 330, 80)
    mask = _rect_to_mask_image(mask_rect, FIXTURE)

    assert mask.pixelColor(900, 720).red() == 255  # dentro del rectángulo
    assert mask.pixelColor(10, 10).red() == 0  # fuera del rectángulo


def test_rect_to_mask_image_missing_source_raises():
    with pytest.raises(InpaintingEngineError):
        _rect_to_mask_image(QRect(0, 0, 10, 10), Path("no_existe.png"))


# --- Camino principal: servidor persistente (rápido, evita reimportar torch por imagen) ---

@patch("watermark_remover.core.inpainting_engine.requests.post")
def test_ioaint_engine_uses_server_when_available(mock_post, tmp_path):
    server = MagicMock()
    server.base_url = "http://127.0.0.1:12345"
    server.ensure_running.return_value = None

    mock_post.return_value = MagicMock(status_code=200, content=FIXTURE.read_bytes())

    engine = IOPaintEngine()
    engine._server = server  # evita arrancar un servidor real en el test

    output_path = tmp_path / "resultado.png"
    result = engine.process(FIXTURE, QRect(850, 700, 330, 80), output_path)

    assert result == output_path
    assert output_path.exists()
    server.ensure_running.assert_called_once()

    sent_json = mock_post.call_args.kwargs["json"]
    assert "image" in sent_json and "mask" in sent_json


@patch("watermark_remover.core.inpainting_engine.requests.post")
def test_ioaint_engine_server_different_extension_is_converted(mock_post, tmp_path):
    """El servidor puede devolver la imagen en otro formato — se combina con Pillow y se
    guarda en el formato de output_path sin necesitar un caso especial de conversión."""
    server = MagicMock()
    server.base_url = "http://127.0.0.1:12345"
    mock_post.return_value = MagicMock(status_code=200, content=FIXTURE.read_bytes())  # PNG real

    engine = IOPaintEngine()
    engine._server = server

    output_path = tmp_path / "resultado.webp"
    result = engine.process(FIXTURE, QRect(850, 700, 330, 80), output_path)

    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0


@patch("watermark_remover.core.inpainting_engine.requests.post")
def test_ioaint_engine_raises_on_server_error_status(mock_post, tmp_path):
    server = MagicMock()
    server.base_url = "http://127.0.0.1:12345"
    mock_post.return_value = MagicMock(status_code=500, text="error interno")

    engine = IOPaintEngine()
    engine._server = server

    # Sin CLI disponible tampoco, para forzar que el error se propague.
    with patch("watermark_remover.core.inpainting_engine._find_iopaint_executable", side_effect=InpaintingEngineError("no CLI")):
        with pytest.raises(InpaintingEngineError):
            engine.process(FIXTURE, QRect(0, 0, 10, 10), tmp_path / "out.png")


# --- Camino de respaldo: un proceso de IOPaint por imagen (si el servidor no arranca) ---

@patch("watermark_remover.core.inpainting_engine.subprocess.run")
@patch("watermark_remover.core.inpainting_engine._find_iopaint_executable", return_value="iopaint")
def test_ioaint_engine_falls_back_to_cli_when_server_fails(mock_find, mock_run, tmp_path):
    def fake_run(cmd, **kwargs):
        out_idx = cmd.index("--output") + 1
        out_dir = Path(cmd[out_idx])
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / FIXTURE.name).write_bytes(FIXTURE.read_bytes())
        return MagicMock(returncode=0, stdout="", stderr="")

    mock_run.side_effect = fake_run

    engine = IOPaintEngine()
    with patch.object(IOPaintEngine, "_process_via_server", side_effect=InpaintingEngineError("servidor no disponible")):
        output_path = tmp_path / "resultado.png"
        result = engine.process(FIXTURE, QRect(850, 700, 330, 80), output_path)

    assert result == output_path
    assert output_path.exists()

    called_cmd = mock_run.call_args.args[0]
    assert "--model" in called_cmd and "migan" in called_cmd
    assert "--device" in called_cmd and "cpu" in called_cmd


@patch("watermark_remover.core.inpainting_engine.subprocess.run")
@patch("watermark_remover.core.inpainting_engine._find_iopaint_executable", return_value="iopaint")
def test_ioaint_engine_cli_raises_on_nonzero_exit(mock_find, mock_run, tmp_path):
    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="modelo no disponible")

    engine = IOPaintEngine()
    with patch.object(IOPaintEngine, "_process_via_server", side_effect=InpaintingEngineError("servidor no disponible")):
        with pytest.raises(InpaintingEngineError):
            engine.process(FIXTURE, QRect(0, 0, 10, 10), tmp_path / "out.png")


def test_ioaint_engine_missing_image_raises(tmp_path):
    engine = IOPaintEngine()
    with pytest.raises(InpaintingEngineError):
        engine.process(Path("no_existe.png"), QRect(0, 0, 10, 10), tmp_path / "out.png")


@patch("watermark_remover.core.inpainting_engine.shutil.which", return_value=None)
def test_find_iopaint_executable_raises_clear_error_when_not_found_anywhere(mock_which, tmp_path, monkeypatch):
    # Ni en PATH, ni junto al intérprete (simulado como un .exe empaquetado sin Scripts/),
    # ni en las carpetas típicas de Windows.
    monkeypatch.setattr("watermark_remover.core.inpainting_engine.sys.executable", str(tmp_path / "App.exe"))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))
    monkeypatch.setenv("APPDATA", str(tmp_path / "roaming"))
    with pytest.raises(InpaintingEngineError, match="pip install iopaint"):
        _find_iopaint_executable()


@patch("watermark_remover.core.inpainting_engine.shutil.which", return_value=None)
def test_find_iopaint_executable_finds_it_in_local_appdata_python(mock_which, tmp_path, monkeypatch):
    # Simula el caso real: el .exe empaquetado no ve `iopaint` en PATH ni junto a sí mismo,
    # pero sí está instalado en la carpeta típica de Python del usuario en Windows.
    monkeypatch.setattr("watermark_remover.core.inpainting_engine.sys.executable", str(tmp_path / "App.exe"))

    scripts_dir = tmp_path / "local" / "Programs" / "Python" / "Python311" / "Scripts"
    scripts_dir.mkdir(parents=True)
    fake_exe = scripts_dir / "iopaint.exe"
    fake_exe.write_bytes(b"fake")

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))
    monkeypatch.setenv("APPDATA", str(tmp_path / "roaming"))

    found = _find_iopaint_executable()
    assert found == str(fake_exe)
