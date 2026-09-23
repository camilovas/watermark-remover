# Definition of Done — Sprint 1

> Ver también: [Plan del sprint](plan.md) · [Estimación del sprint](estimation.md) · [DoD base del proyecto](../../dod_base.md)

Extiende el [DoD base](../../dod_base.md) con lo específico de este sprint (primer código de producto/UI):

1. Las 3 historias (HU-4, HU-5, HU-7) cumplen sus criterios de aceptación del [Product Backlog](../../product_backlog.md).
2. Flujo demostrable de punta a punta: abrir la app → cargar 1+ imágenes → marcar máscara manual → procesar → ver resultado antes/después → guardar. Probado manualmente, no solo con tests.
3. La UI no se congela (freeze) durante el procesamiento (verificado corriendo en un equipo con CPU modesta).
4. El procesamiento corre 100% local, sin necesitar Docker ni conexión a internet.
5. Tests unitarios de `image_utils`, conversión canvas→máscara, y `IOPaintEngine` (mockeado) en verde, local y en Docker.
6. Manejo de errores validado manualmente con al menos un caso real (ej. imagen corrupta, formato no soportado).
