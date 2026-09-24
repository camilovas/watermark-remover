# Definition of Done — Sprint 2

> Ver también: [Plan del sprint](plan.md) · [Estimación del sprint](estimation.md) · [DoD base del proyecto](../../dod_base.md)

Extiende el [DoD base](../../dod_base.md) con lo específico de este sprint:

1. ✅ HU-6 y HU-8 cumplen sus criterios de aceptación del [Product Backlog](../../product_backlog.md).
2. ✅ **Confirmado**: con Ollama no disponible, `create_detector()` devuelve `NullDetector` (verificado con `is_available() == False` mockeado — misma ruta de código que si Ollama estuviera realmente apagado) y la app sigue operando sin errores ni referencias rotas.
3. ✅ Con Ollama disponible (real, corriendo local), se validó una llamada real: `create_detector()` resuelve en ~2s, `detect()` toma ~56s y devuelve un rect — se confirmó en el código que `OllamaClient` reduce la imagen a miniatura (~512px) antes de enviarla, nunca la imagen completa.
4. ✅ Progreso, cancelación y resiliencia a errores verificados en dos niveles complementarios: `tests/test_batch_processor.py` (5 imágenes, engine mockeado — cancelación a mitad de lote, error en una imagen no detiene el resto) + prueba funcional real con IOPaint real sobre 2 imágenes (progreso 1/2 → 2/2, ambas guardadas correctamente).
5. ✅ 33 tests (`BatchProcessor`, `OllamaWatermarkDetector`/`NullDetector`, más toda la suite previa) en verde, local (2.5s) y en Docker (4.81s).

**Sprint 2: completado.**
