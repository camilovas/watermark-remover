from unittest.mock import MagicMock, patch

import pytest
import requests

from watermark_remover.core.inpainting_engine import InpaintingEngineError
from watermark_remover.core.iopaint_server import IOPaintServer


@patch("watermark_remover.core.iopaint_server.requests.get")
@patch("watermark_remover.core.iopaint_server.subprocess.Popen")
@patch("watermark_remover.core.iopaint_server._find_iopaint_executable", return_value="iopaint")
@patch("watermark_remover.core.iopaint_server._find_free_port", return_value=54321)
def test_ensure_running_starts_process_and_waits_for_health_check(mock_port, mock_find, mock_popen, mock_get):
    process = MagicMock()
    process.poll.return_value = None  # sigue vivo
    mock_popen.return_value = process
    mock_get.return_value = MagicMock(status_code=200)

    server = IOPaintServer(model="migan")
    server.ensure_running()

    mock_popen.assert_called_once()
    called_cmd = mock_popen.call_args.args[0]
    assert "start" in called_cmd
    assert "--model" in called_cmd and "migan" in called_cmd
    assert "--port" in called_cmd and "54321" in called_cmd
    assert server.base_url == "http://127.0.0.1:54321"


@patch("watermark_remover.core.iopaint_server.requests.get")
def test_ensure_running_skips_relaunch_if_already_up(mock_get):
    mock_get.return_value = MagicMock(status_code=200)

    server = IOPaintServer()
    fake_process = MagicMock()
    fake_process.poll.return_value = None
    server._process = fake_process
    server.port = 9999

    with patch("watermark_remover.core.iopaint_server.subprocess.Popen") as mock_popen:
        server.ensure_running()
        mock_popen.assert_not_called()


@patch("watermark_remover.core.iopaint_server.requests.get", side_effect=requests.exceptions.ConnectionError("no responde"))
@patch("watermark_remover.core.iopaint_server.subprocess.Popen")
@patch("watermark_remover.core.iopaint_server._find_iopaint_executable", return_value="iopaint")
@patch("watermark_remover.core.iopaint_server._find_free_port", return_value=54321)
@patch("watermark_remover.core.iopaint_server.SERVER_STARTUP_TIMEOUT_SECONDS", 1)
@patch("watermark_remover.core.iopaint_server.SERVER_POLL_INTERVAL_SECONDS", 0.1)
def test_ensure_running_raises_if_server_never_responds(mock_port, mock_find, mock_popen, mock_get):
    process = MagicMock()
    process.poll.return_value = None  # el proceso sigue "vivo" pero nunca contesta
    mock_popen.return_value = process

    server = IOPaintServer()
    with pytest.raises(InpaintingEngineError):
        server.ensure_running()


def test_shutdown_terminates_running_process():
    server = IOPaintServer()
    process = MagicMock()
    process.poll.return_value = None
    server._process = process

    server.shutdown()

    process.terminate.assert_called_once()
    assert server._process is None


def test_shutdown_noop_when_nothing_running():
    server = IOPaintServer()
    server.shutdown()  # no debe lanzar excepción
