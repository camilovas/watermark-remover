# Sprint 2 — Lotes + asistencia opcional de Ollama

> Ver también: [Estimación del sprint](estimation.md) · [Definition of Done del sprint](definition_of_done.md) · [Roadmap](../../roadmap.md) · [Product Backlog](../../product_backlog.md)

**Objetivo del sprint:** escalar el flujo validado en Sprint 1 a procesamiento por lotes, y sumar la detección automática de región vía Ollama como mejora opcional (nunca obligatoria).

## Alcance (historias) y desglose de tareas

### HU-6: Sugerencia automática de región vía Ollama
- [ ] Implementar `OllamaClient` (`services/ollama_client.py`): reduce imagen a miniatura (~512px), llama a API con modelo de visión local
- [ ] Implementar `OllamaWatermarkDetector` (`core/watermark_detector.py`) que parsea la respuesta a un bounding box
- [ ] Implementar `NullDetector` como fallback cuando Ollama no está disponible
- [ ] Botón "Detectar automáticamente" en la UI, conectado al detector activo (real o Null)
- [ ] Pre-cargar el bounding box sugerido en el `MaskEditor` (el usuario lo puede ajustar después)
- [ ] Manejar errores de red/timeout (Ollama no responde o el host configurado no existe) sin crashear la app
- [ ] Ocultar/deshabilitar el botón si Ollama no está disponible (verificación vía `services/config.py`)
- [ ] Tests: mockear `OllamaClient`, verificar bbox esperado y fallback a `NullDetector`

### HU-8: Procesamiento por lotes (progreso + cancelar)
- [ ] Implementar `BatchProcessor` (`core/batch_processor.py`) en `QThread`, con cola de `ImageItem`
- [ ] Emitir señales de progreso (ítem actual, X de N) hacia la UI
- [ ] Implementar `ProgressDialog` con barra global y botón cancelar
- [ ] Cancelación cooperativa (chequeo entre imágenes, no corrompe las ya guardadas)
- [ ] Capturar errores por imagen individual sin detener el lote; acumular en lista de resultados
- [ ] Mostrar resumen final (éxitos/errores) al terminar el lote
- [ ] Tests: batch con engine mock que falla en la imagen N (continúa y reporta); test de cancelación a mitad de lote

## Fuera de alcance en Sprint 2
- Empaquetado como ejecutable (HU-9, Sprint 3).
- Cierre/endurecimiento final de la suite de pruebas (HU-10, Sprint 3) — aunque cada HU de este sprint ya trae sus propios tests, por DoD.
