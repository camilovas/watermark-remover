import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from watermark_remover.utils.file_utils import safe_output_path


def test_safe_output_path_default_suffix(tmp_path):
    original = tmp_path / "foto.png"
    original.write_bytes(b"fake")
    result = safe_output_path(original)
    assert result.name == "foto_sin_marca.png"


def test_safe_output_path_avoids_overwrite(tmp_path):
    original = tmp_path / "foto.png"
    original.write_bytes(b"fake")
    (tmp_path / "foto_sin_marca.png").write_bytes(b"existe")

    result = safe_output_path(original)
    assert result.name == "foto_sin_marca_1.png"
    assert not result.exists()


def test_safe_output_path_custom_dir(tmp_path):
    original = tmp_path / "sub" / "foto.png"
    original.parent.mkdir()
    original.write_bytes(b"fake")
    out_dir = tmp_path / "salida"

    result = safe_output_path(original, output_dir=out_dir)
    assert result.parent == out_dir
