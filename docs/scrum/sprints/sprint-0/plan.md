# Sprint 0 — Fundación técnica

> Ver también: [Estimación del sprint](estimation.md) · [Definition of Done del sprint](definition_of_done.md) · [Product Backlog](../../product_backlog.md) · [DoD base](../../dod_base.md)

**Objetivo del sprint:** dejar el proyecto listo para empezar a construir funcionalidad: entorno de pruebas reproducible, validación de viabilidad del motor de IA local y de la integración con Ollama.

## Alcance (historias) y desglose de tareas

### HU-1: Entorno de desarrollo y pruebas reproducible (Docker solo para tests) ✅
- [x] Crear `requirements.txt` / `requirements-dev.txt`
- [x] Escribir `docker/Dockerfile.test`
- [x] Escribir `docker-compose.yml` (servicio `test`)
- [x] Configurar pytest básico (archivo de config + test placeholder)
- [x] Documentar en README cómo correr tests local y con Docker
- [x] Verificar que `docker-compose up test` corre sin errores en una máquina limpia — 1 passed

### HU-2: Spike — validar motor de inpainting local (IOPaint/LaMa) ✅
- [x] Instalar IOPaint en entorno virtual local (v1.6.0)
- [x] Descargar/cachear el modelo LaMa (`big-lama.pt`, ~200MB, una sola vez)
- [x] Preparar imagen de prueba con marca de agua conocida (`tests/fixtures/sample_watermarked.png`, sintética) + máscara (`sample_watermarked_mask.png`)
- [x] Ejecutar IOPaint (CLI local) sobre la imagen con la máscara
- [x] Medir tiempo de procesamiento — ~25s totales, ~7s de inferencia pura (modelo cacheado, CPU, imagen 1200×800)
- [x] Confirmado funcionamiento con el modelo ya cacheado localmente (no requiere red tras la descarga inicial)
- [x] Documentar resultados en `docs/research/best_practices.md` — incluye evaluación visual de calidad

### HU-3: Spike — integración con Ollama local ✅
- [x] Confirmar que Ollama está corriendo (`ollama list`) y descargar un modelo de visión (`ollama pull moondream`, y `llava:7b` como comparación)
- [x] Generar miniatura (~512px) de una imagen de prueba
- [x] Script mínimo que llame a la API REST de Ollama pidiendo bounding box de la marca de agua
- [x] Registrar tiempo de respuesta y evaluar la precisión del bounding box devuelto — ver hallazgos en `docs/research/best_practices.md` (bug de GPU/Vulkan encontrado y resuelto con `num_gpu: 0`; comparación moondream vs llava:7b)
- [x] Probar el comportamiento cuando Ollama no está disponible (debe degradar sin crashear) — `ConnectionError` limpio, manejable por `NullDetector`
- [x] Documentar cómo apuntar a un host de Ollama remoto en la red (`OLLAMA_HOST`) — ver `docs/architecture/overview.md`
- [x] Documentar hallazgos en `docs/research/best_practices.md`

## Entregables esperados
- Repositorio con estructura base (`src/`, `tests/`, `docs/`, `docker/`).
- `docker-compose.yml` + `docker/Dockerfile.test` funcionando.
- Documento de resultados de los spikes (viabilidad, tiempos) agregado a `docs/research/best_practices.md`.

## Fuera de alcance en Sprint 0
- UI final, selección múltiple real, empaquetado con PyInstaller (eso empieza en el Sprint 1, Épica 2).
