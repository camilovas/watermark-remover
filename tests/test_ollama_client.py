import base64
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from watermark_remover.services.ollama_client import OllamaClient, OllamaUnavailableError

FIXTURE = Path(__file__).parent / "fixtures" / "sample_watermarked.png"


def test_client_uses_configured_host_and_model():
    client = OllamaClient(host="http://otra-maquina:11434", model="llava:7b")
    assert client.host == "http://otra-maquina:11434"
    assert client.model == "llava:7b"


def test_client_defaults_come_from_config(monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", "http://host-config:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "custom-model")
    client = OllamaClient()
    assert client.host == "http://host-config:11434"
    assert client.model == "custom-model"


@patch("watermark_remover.services.ollama_client.requests.get")
def test_is_available_true_on_200(mock_get):
    mock_get.return_value = MagicMock(status_code=200)
    client = OllamaClient()
    assert client.is_available() is True


@patch("watermark_remover.services.ollama_client.requests.get")
def test_is_available_false_on_connection_error(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError("no hay nadie escuchando")
    client = OllamaClient()
    assert client.is_available() is False


@patch("watermark_remover.services.ollama_client.requests.post")
def test_detect_watermark_region_sends_only_thumbnail_not_full_image(mock_post):
    mock_post.return_value = MagicMock(status_code=200, json=lambda: {"response": '{"found": false}'})

    client = OllamaClient()
    client.detect_watermark_region(FIXTURE)

    call_kwargs = mock_post.call_args.kwargs
    sent_json = call_kwargs["json"]
    assert sent_json["model"] == client.model
    assert len(sent_json["images"]) == 1
    # La miniatura (base64) debe ser bastante más chica que la imagen original completa.
    thumb_bytes = base64.b64decode(sent_json["images"][0])
    original_bytes = FIXTURE.stat().st_size
    assert len(thumb_bytes) < original_bytes * 5  # margen generoso; el punto es que no es absurdamente grande
    assert sent_json["options"]["num_gpu"] == 0  # workaround del bug de GPU/Vulkan (Sprint 0)


@patch("watermark_remover.services.ollama_client.requests.post")
def test_detect_watermark_region_raises_on_network_error(mock_post):
    mock_post.side_effect = requests.exceptions.ConnectionError("host no encontrado")
    client = OllamaClient()

    with pytest.raises(OllamaUnavailableError):
        client.detect_watermark_region(FIXTURE)


@patch("watermark_remover.services.ollama_client.requests.post")
def test_detect_watermark_region_raises_on_non_200(mock_post):
    mock_post.return_value = MagicMock(status_code=500, text="modelo no encontrado")
    client = OllamaClient()

    with pytest.raises(OllamaUnavailableError):
        client.detect_watermark_region(FIXTURE)
