from pathlib import Path


def safe_output_path(original_path: str | Path, suffix: str = "_sin_marca", output_dir: str | Path | None = None) -> Path:
    """Genera una ruta de salida que no sobrescribe archivos existentes."""
    original = Path(original_path)
    target_dir = Path(output_dir) if output_dir else original.parent
    candidate = target_dir / f"{original.stem}{suffix}{original.suffix}"

    counter = 1
    while candidate.exists():
        candidate = target_dir / f"{original.stem}{suffix}_{counter}{original.suffix}"
        counter += 1

    return candidate
