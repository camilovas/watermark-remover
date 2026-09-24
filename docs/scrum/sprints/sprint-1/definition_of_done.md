# Definition of Done — Sprint 1

> Ver también: [Plan del sprint](plan.md) · [Estimación del sprint](estimation.md) · [DoD base del proyecto](../../dod_base.md)

Extiende el [DoD base](../../dod_base.md) con lo específico de este sprint (primer código de producto/UI):

1. ✅ Las 3 historias (HU-4, HU-5, HU-7) cumplen sus criterios de aceptación del [Product Backlog](../../product_backlog.md).
2. ✅ Flujo demostrable de punta a punta: cargar imagen → marcar máscara → procesar → ver resultado antes/después → guardar. Probado con un script funcional real (no solo mocks): 21.8s de principio a fin sobre la imagen de prueba.
3. ✅ La UI no se congela durante el procesamiento — corre en `QThreadPool`, verificado que la app sigue respondiendo (`app.processEvents()`) mientras procesa.
4. ✅ El procesamiento corre 100% local (IOPaint/LaMa vía CLI local), sin necesitar Docker ni conexión a internet tras la instalación inicial.
5. ✅ 19 tests unitarios (`image_utils`, `file_utils`, conversión canvas→máscara, `ImageListWidget`, `IOPaintEngine` mockeado, `processing_worker`) en verde, tanto local (1.49s) como en Docker (3.12s).
6. ✅ Manejo de errores validado: formato no soportado (`test_add_unsupported_format_is_rejected`), imagen inválida (`test_make_thumbnail_invalid_image_raises`), imagen faltante y falla del motor (`test_ioaint_engine_missing_image_raises`, `test_ioaint_engine_raises_on_nonzero_exit`) — todos con casos reales, no solo lógica mockeada.

**Bug real encontrado y corregido en este sprint:** el procesamiento en background (`QThreadPool`) nunca completaba porque la tarea se perdía por garbage collection antes de terminar — ver detalle en [plan.md](plan.md). Se corrigió y se agregó test de regresión.

**Sprint 1: completado.**
