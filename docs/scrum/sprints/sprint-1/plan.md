# Sprint 1 — Flujo end-to-end de una sola imagen

> Ver también: [Estimación del sprint](estimation.md) · [Definition of Done del sprint](definition_of_done.md) · [Roadmap](../../roadmap.md) · [Product Backlog](../../product_backlog.md)

**Objetivo del sprint:** que el usuario pueda cargar imágenes, marcar manualmente la región de la marca de agua y obtener el resultado procesado localmente — el primer incremento demostrable del producto, sin depender de Ollama.

## Alcance (historias) y desglose de tareas

### HU-4: Selección múltiple de imágenes ✅
- [x] Crear `MainWindow` esqueleto (PySide6) con layout base
- [x] Botón "Agregar imágenes" con `QFileDialog` en modo multi-select
- [x] Soportar drag & drop de archivos sobre la ventana/lista
- [x] Crear `ImageListWidget` con miniaturas (galería)
- [x] Validar formatos soportados (PNG, JPG/JPEG, WEBP) y mostrar error para no soportados
- [x] Generar thumbnails de forma eficiente (`utils/image_utils.py`) sin bloquear la UI
- [x] Tests: filtrado de formatos, agregar/quitar imágenes de la lista (`tests/test_image_list_widget.py`, `tests/test_image_utils.py`)

### HU-5: Marcado manual de región (mask editor) ✅
- [x] Crear `PreviewCanvas` que muestre la imagen seleccionada
- [x] Dibujar rectángulo de máscara con el mouse (press/move/release)
- [x] Mover y redimensionar el rectángulo (handles en las esquinas)
- [x] Botón "limpiar máscara" / deshacer
- [x] Convertir el rectángulo dibujado a máscara binaria para pasar al motor
- [x] Tests: lógica de conversión canvas → máscara, independiente de la UI real (`tests/test_inpainting_engine.py::test_rect_to_mask_image_*`)

### HU-7: Procesamiento de imagen (inpainting local) ✅
- [x] Definir interfaz `InpaintingEngine` (`core/inpainting_engine.py`)
- [x] Implementar `IOPaintEngine` (invoca IOPaint local con imagen + máscara)
- [x] Manejar conversión de formatos/resoluciones de entrada-salida
- [x] Barra de progreso indeterminada durante el procesamiento (`QThreadPool`, no bloquea UI)
- [x] Vista de comparación antes/después
- [x] Botón "Guardar resultado" con nombre de archivo seguro (`utils/file_utils.py`, evita sobrescritura)
- [x] Manejo de errores (imagen corrupta, motor no disponible) con mensaje claro al usuario
- [x] Tests: `IOPaintEngine` mockeado, verificar llamada correcta y manejo de error (`tests/test_inpainting_engine.py`, `tests/test_processing_worker.py`)

**Bug encontrado y corregido durante la implementación:** el procesamiento en `QThreadPool` nunca terminaba — la tarea (`QRunnable`) se perdía por garbage collection de Python antes de que el hilo en segundo plano terminara, porque `process_async()` no mantenía ninguna referencia viva a la tarea tras retornar. Se corrigió manteniendo las tareas activas en un `set` module-level hasta que emiten su señal de fin. Se agregó `tests/test_processing_worker.py` como test de regresión (fuerza un `gc.collect()` a mitad del procesamiento).

## Fuera de alcance en Sprint 1
- Procesamiento por lotes (HU-8, Sprint 2).
- Sugerencia automática de región vía Ollama (HU-6, Sprint 2).
- Empaquetado como ejecutable (HU-9, Sprint 3).
