from pathlib import Path
from unittest.mock import MagicMock

from watermark_remover.core.watermark_detector import (
    NullDetector,
    OllamaWatermarkDetector,
    _box_to_rect,
    _parse_box,
    create_detector,
)
from watermark_remover.services.ollama_client import OllamaUnavailableError

FIXTURE = Path(__file__).parent / "fixtures" / "sample_watermarked.png"


def test_null_detector_never_calls_network_and_returns_none():
    detector = NullDetector()
    assert detector.detect(FIXTURE) is None


def test_parse_box_from_well_formed_json():
    box = _parse_box('{"found": true, "box": [0.1, 0.2, 0.3, 0.4]}')
    assert box == (0.1, 0.2, 0.3, 0.4)


def test_parse_box_from_not_found_json():
    assert _parse_box('{"found": false}') is None


def test_parse_box_tolerant_to_raw_list_without_json_wrapper():
    # Comportamiento observado en el spike: algunos modelos ignoran el formato pedido.
    box = _parse_box(" [0.24, 0.68, 0.83, 0.87] ")
    assert box == (0.24, 0.68, 0.83, 0.87)


def test_parse_box_unparseable_returns_none():
    assert _parse_box("no encontré nada relevante en la imagen") is None


def test_box_to_rect_normalized_scales_to_image_size():
    rect = _box_to_rect((0.1, 0.2, 0.5, 0.6), image_width=1000, image_height=500)
    assert rect.left() == 100
    assert rect.top() == 100
    assert rect.width() == 400
    assert rect.height() == 200


def test_box_to_rect_pixel_values_used_directly():
    rect = _box_to_rect((100, 200, 300, 250), image_width=1000, image_height=500)
    assert rect.left() == 100
    assert rect.top() == 200
    assert rect.width() == 200
    assert rect.height() == 50


def test_ollama_detector_returns_rect_from_mocked_client():
    client = MagicMock()
    client.detect_watermark_region.return_value = '{"found": true, "box": [0.5, 0.5, 0.9, 0.9]}'

    detector = OllamaWatermarkDetector(client=client)
    rect = detector.detect(FIXTURE)

    assert rect is not None
    assert rect.width() > 0 and rect.height() > 0


def test_ollama_detector_returns_none_when_ollama_unavailable():
    client = MagicMock()
    client.detect_watermark_region.side_effect = OllamaUnavailableError("no responde")

    detector = OllamaWatermarkDetector(client=client)
    assert detector.detect(FIXTURE) is None


def test_create_detector_falls_back_to_null_when_unavailable():
    client = MagicMock()
    client.is_available.return_value = False

    detector = create_detector(client=client)
    assert isinstance(detector, NullDetector)


def test_create_detector_returns_ollama_detector_when_available():
    client = MagicMock()
    client.is_available.return_value = True

    detector = create_detector(client=client)
    assert isinstance(detector, OllamaWatermarkDetector)
