# Sprint 2 — Lotes + asistencia opcional de Ollama

> Ver también: [Estimación del sprint](estimation.md) · [Definition of Done del sprint](definition_of_done.md) · [Roadmap](../../roadmap.md) · [Product Backlog](../../product_backlog.md)

**Objetivo del sprint:** escalar el flujo validado en Sprint 1 a procesamiento por lotes, y sumar la detección automática de región vía Ollama como mejora opcional (nunca obligatoria).

## Alcance (historias) y desglose de tareas

### HU-6: Sugerencia automática de región vía Ollama ✅
- [x] Implementar `OllamaClient` (`services/ollama_client.py`): reduce imagen a miniatura (~512px), llama a API con modelo de visión local, forzando `num_gpu: 0` (workaround del bug encontrado en Sprint 0)
- [x] Implementar `OllamaWatermarkDetector` (`core/watermark_detector.py`) que parsea la respuesta a un bounding box (tolerante: JSON bien formado o solo una lista de 4 números; normalizado 0-1 o píxeles)
- [x] Implementar `NullDetector` como fallback cuando Ollama no está disponible
- [x] Botón "Detectar automáticamente" en la UI, conectado al detector activo (real o Null), oculto si no hay Ollama disponible
- [x] Pre-cargar el bounding box sugerido en el `MaskEditor` (el usuario lo puede ajustar después)
- [x] Manejar errores de red/timeout (`OllamaUnavailableError`) sin crashear la app
- [x] Ocultar/deshabilitar el botón si Ollama no está disponible (`services/config.py` + `create_detector()`)
- [x] Tests: mockear `OllamaClient`, verificar bbox esperado y fallback a `NullDetector` (`tests/test_watermark_detector.py`, 11 tests)
- [x] Probado end-to-end con Ollama real: detector se resuelve en ~2s, detección real toma ~56s y devuelve un rect (precisión limitada, consistente con el spike de Sprint 0 — por eso el usuario siempre puede ajustar la sugerencia)

### HU-8: Procesamiento por lotes (progreso + cancelar) ✅
- [x] Implementar `BatchProcessor` (`core/batch_processor.py`) en `QThread`, con cola de `ImageItem`
- [x] Emitir señales de progreso (ítem actual, X de N) hacia la UI
- [x] Implementar `ProgressDialog` con barra global y botón cancelar
- [x] Cancelación cooperativa (chequeo entre imágenes, no corrompe las ya guardadas)
- [x] Capturar errores por imagen individual sin detener el lote; acumular en lista de resultados
- [x] Mostrar resumen final (éxitos/errores) al terminar el lote
- [x] Tests: batch con engine mock que falla en la imagen N (continúa y reporta); test de cancelación a mitad de lote (`tests/test_batch_processor.py`, 3 tests)
- [x] Probado end-to-end con IOPaint real sobre 2 imágenes: ambas procesadas correctamente, progreso 1/2 → 2/2

**Hallazgo de rendimiento (no bloqueante):** cada imagen del lote recarga el modelo LaMa desde cero (el motor invoca el CLI de IOPaint por subprocess en cada llamada, sin servidor persistente) — ~35s/imagen en el lote vs ~25s de una sola imagen suelta. Optimización futura: usar el modo servidor de IOPaint (`iopaint start`) en vez de `iopaint run` por imagen, para mantener el modelo cargado entre llamadas. Queda fuera del alcance de este sprint (no es un requisito de HU-8).

## Fuera de alcance en Sprint 2
- Empaquetado como ejecutable (HU-9, Sprint 3).
- Cierre/endurecimiento final de la suite de pruebas (HU-10, Sprint 3) — aunque cada HU de este sprint ya trae sus propios tests, por DoD.
