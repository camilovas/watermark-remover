# Sprint 0 — Fundación técnica

> Ver también: [Estimación del sprint](estimation.md) · [Definition of Done del sprint](definition_of_done.md) · [Product Backlog](../../product_backlog.md) · [DoD base](../../dod_base.md)

**Objetivo del sprint:** dejar el proyecto listo para empezar a construir funcionalidad: entorno de pruebas reproducible, validación de viabilidad del motor de IA local y de la integración barata con Claude.

## Alcance (historias) y desglose de tareas

### HU-1: Entorno de desarrollo y pruebas reproducible (Docker solo para tests)
- [ ] Crear `requirements.txt` / `requirements-dev.txt`
- [ ] Escribir `docker/Dockerfile.test`
- [ ] Escribir `docker-compose.yml` (servicio `test`)
- [ ] Configurar pytest básico (archivo de config + test placeholder)
- [ ] Documentar en README cómo correr tests local y con Docker
- [ ] Verificar que `docker-compose up test` corre sin errores en una máquina limpia

### HU-2: Spike — validar motor de inpainting local (IOPaint/LaMa)
- [ ] Instalar IOPaint en entorno virtual local
- [ ] Descargar/cachear el modelo LaMa
- [ ] Preparar 3-5 imágenes de prueba con marca de agua conocida
- [ ] Ejecutar IOPaint (CLI o API local) sobre una imagen con máscara manual
- [ ] Medir tiempo de procesamiento y uso de RAM/CPU
- [ ] Repetir sin conexión a internet para confirmar funcionamiento offline
- [ ] Documentar resultados en `docs/research/best_practices.md`

### HU-3: Spike — integración de bajo costo con Claude API
- [ ] Generar miniatura (~512px) de una imagen de prueba
- [ ] Script mínimo que llame al SDK de Anthropic (modelo Haiku) pidiendo bounding box de la marca de agua
- [ ] Registrar tokens de entrada/salida y costo estimado por llamada
- [ ] Probar el comportamiento sin API key configurada (debe degradar sin crashear)
- [ ] Documentar hallazgos en `docs/research/best_practices.md`

## Entregables esperados
- Repositorio con estructura base (`src/`, `tests/`, `docs/`, `docker/`).
- `docker-compose.yml` + `docker/Dockerfile.test` funcionando.
- Documento de resultados de los spikes (viabilidad, tiempos, costos) agregado a `docs/research/best_practices.md`.

## Fuera de alcance en Sprint 0
- UI final, selección múltiple real, empaquetado con PyInstaller (eso empieza en el Sprint 1, Épica 2).
