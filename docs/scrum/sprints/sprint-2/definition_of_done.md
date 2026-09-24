# Definition of Done — Sprint 2

> Ver también: [Plan del sprint](plan.md) · [Estimación del sprint](estimation.md) · [DoD base del proyecto](../../dod_base.md)

Extiende el [DoD base](../../dod_base.md) con lo específico de este sprint:

1. HU-6 y HU-8 cumplen sus criterios de aceptación del [Product Backlog](../../product_backlog.md).
2. **Confirmado explícitamente**: con Ollama **no disponible** (apagado o sin configurar), la app procesa lotes completos sin errores ni referencias rotas (usa `NullDetector` de forma transparente).
3. Con Ollama disponible, se validó al menos una vez la llamada real al modelo de visión local (`moondream`) y se verificó que solo se envía la miniatura (no la imagen completa) — inspeccionable en logs/tráfico de red.
4. Probado un lote de al menos 5 imágenes: progreso visible, cancelación a mitad de lote no corrompe archivos ya guardados, y un error forzado en una imagen no detiene el resto.
5. Tests de `BatchProcessor` y `OllamaWatermarkDetector`/`NullDetector` en verde, local y en Docker.
