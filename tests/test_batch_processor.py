import time
from pathlib import Path
from unittest.mock import MagicMock

from PySide6.QtCore import QRect
from PySide6.QtWidgets import QApplication

from watermark_remover.core.batch_processor import BatchProcessor
from watermark_remover.core.image_item import ImageItem, ImageStatus
from watermark_remover.core.inpainting_engine import InpaintingEngineError

FIXTURE = Path(__file__).parent / "fixtures" / "sample_watermarked.png"


def _make_items(n: int) -> list[ImageItem]:
    return [ImageItem(path=FIXTURE) for _ in range(n)]


def _wait_until(predicate, timeout=5.0):
    """Bombea el loop de eventos hasta que predicate() sea verdadero.

    No basta con esperar mientras thread.isRunning(): con un motor simulado el hilo puede
    terminar antes de que el test llegue a este punto, y la señal batch_finished (emitida
    desde otro hilo, entregada por conexión en cola) solo se procesa llamando processEvents().
    """
    app = QApplication.instance()
    start = time.time()
    while not predicate() and time.time() - start < timeout:
        app.processEvents()
        time.sleep(0.01)


def test_batch_continues_after_failure_on_one_image():
    items = _make_items(3)

    engine = MagicMock()
    call_count = {"n": 0}

    def fake_process(path, mask_rect, output_path):
        call_count["n"] += 1
        if call_count["n"] == 2:
            raise InpaintingEngineError("falló la imagen 2")
        return output_path

    engine.process.side_effect = fake_process

    results_holder = {}

    def on_batch_finished(results):
        results_holder["results"] = results

    thread = BatchProcessor(engine, items, default_mask_rect=QRect(0, 0, 10, 10))
    thread.batch_finished.connect(on_batch_finished)
    thread.start()
    _wait_until(lambda: "results" in results_holder)

    results = results_holder["results"]
    assert len(results) == 3
    assert engine.process.call_count == 3  # no se detuvo tras el fallo
    assert [r.success for r in results] == [True, False, True]
    assert items[1].status == ImageStatus.ERROR
    assert items[0].status == ImageStatus.DONE
    assert items[2].status == ImageStatus.DONE


def test_batch_cancellation_stops_before_remaining_images():
    items = _make_items(5)
    engine = MagicMock()

    def slow_process(path, mask_rect, output_path):
        # Simula trabajo real para darle al hilo principal ventana de procesar la señal
        # item_started y disparar cancel() antes de que el lote termine solo.
        time.sleep(0.1)
        return output_path

    engine.process.side_effect = slow_process

    progress_events = []

    def on_item_started(current, total, name):
        progress_events.append(current)
        if current == 2:
            thread.cancel()

    results_holder = {}

    thread = BatchProcessor(engine, items, default_mask_rect=QRect(0, 0, 10, 10))
    thread.item_started.connect(on_item_started)
    thread.batch_finished.connect(lambda results: results_holder.update(results=results))
    thread.start()
    _wait_until(lambda: "results" in results_holder)

    results = results_holder["results"]
    assert len(results) < len(items)  # se canceló antes de terminar todas
    assert engine.process.call_count == len(results)


def test_batch_run_body_directly_for_coverage_and_cancel_before_start():
    """Invoca run() de forma síncrona (sin start()) para que coverage la rastree
    (coverage no instrumenta de forma confiable el código ejecutado dentro de un
    QThread real) y de paso cubre el camino donde se cancela antes de procesar nada."""
    items = _make_items(2)
    engine = MagicMock()
    engine.process.side_effect = lambda path, mask_rect, output_path: output_path

    thread = BatchProcessor(engine, items, default_mask_rect=QRect(0, 0, 10, 10))
    results_holder = {}
    thread.batch_finished.connect(lambda results: results_holder.update(results=results))

    thread.run()  # ejecución síncrona, en el hilo del test

    assert results_holder["results"][0].success is True
    assert engine.process.call_count == 2

    # Cancelar antes de correr: el lote no debe procesar nada.
    items2 = _make_items(2)
    thread2 = BatchProcessor(engine, items2, default_mask_rect=QRect(0, 0, 10, 10))
    thread2.cancel()
    results_holder2 = {}
    thread2.batch_finished.connect(lambda results: results_holder2.update(results=results))
    thread2.run()

    assert results_holder2["results"] == []


def test_batch_uses_per_item_mask_when_present():
    items = _make_items(1)
    items[0].mask_rect = QRect(5, 5, 20, 20)
    engine = MagicMock()
    engine.process.side_effect = lambda path, mask_rect, output_path: output_path

    thread = BatchProcessor(engine, items, default_mask_rect=QRect(0, 0, 1, 1))
    thread.start()
    _wait_until(lambda: engine.process.call_count > 0)

    used_mask = engine.process.call_args.args[1]
    assert used_mask == QRect(5, 5, 20, 20)
