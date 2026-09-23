# Sprint 1 — Flujo end-to-end de una sola imagen

> Ver también: [Estimación del sprint](estimation.md) · [Definition of Done del sprint](definition_of_done.md) · [Roadmap](../../roadmap.md) · [Product Backlog](../../product_backlog.md)

**Objetivo del sprint:** que el usuario pueda cargar imágenes, marcar manualmente la región de la marca de agua y obtener el resultado procesado localmente — el primer incremento demostrable del producto, sin depender de Claude.

## Alcance (historias) y desglose de tareas

### HU-4: Selección múltiple de imágenes
- [ ] Crear `MainWindow` esqueleto (PySide6) con layout base
- [ ] Botón "Agregar imágenes" con `QFileDialog` en modo multi-select
- [ ] Soportar drag & drop de archivos sobre la ventana/lista
- [ ] Crear `ImageListWidget` con miniaturas (galería)
- [ ] Validar formatos soportados (PNG, JPG/JPEG, WEBP) y mostrar error para no soportados
- [ ] Generar thumbnails de forma eficiente (`utils/image_utils.py`) sin bloquear la UI
- [ ] Tests: filtrado de formatos, agregar/quitar imágenes de la lista

### HU-5: Marcado manual de región (mask editor)
- [ ] Crear `PreviewCanvas` que muestre la imagen seleccionada
- [ ] Dibujar rectángulo de máscara con el mouse (press/move/release)
- [ ] Mover y redimensionar el rectángulo (handles en las esquinas)
- [ ] Botón "limpiar máscara" / deshacer
- [ ] Convertir el rectángulo dibujado a máscara binaria para pasar al motor
- [ ] Tests: lógica de conversión canvas → máscara, independiente de la UI real

### HU-7: Procesamiento de imagen (inpainting local)
- [ ] Definir interfaz `InpaintingEngine` (`core/inpainting_engine.py`)
- [ ] Implementar `IOPaintEngine` (invoca IOPaint local con imagen + máscara)
- [ ] Manejar conversión de formatos/resoluciones de entrada-salida
- [ ] Barra de progreso indeterminada durante el procesamiento (correr en `QThread`, no bloquear UI)
- [ ] Vista de comparación antes/después
- [ ] Botón "Guardar resultado" con nombre de archivo seguro (`utils/file_utils.py`, evita sobrescritura)
- [ ] Manejo de errores (imagen corrupta, motor no disponible) con mensaje claro al usuario
- [ ] Tests: `IOPaintEngine` mockeado, verificar llamada correcta y manejo de error

## Fuera de alcance en Sprint 1
- Procesamiento por lotes (HU-8, Sprint 2).
- Sugerencia automática de región vía Claude (HU-6, Sprint 2).
- Empaquetado como ejecutable (HU-9, Sprint 3).
