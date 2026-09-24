import os

DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "moondream"


def get_ollama_host() -> str:
    """Host de Ollama a usar. Configurable vía OLLAMA_HOST para apuntar a otra
    máquina de la red local (ver docs/architecture/overview.md)."""
    return os.environ.get("OLLAMA_HOST", DEFAULT_OLLAMA_HOST)


def get_ollama_model() -> str:
    return os.environ.get("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
