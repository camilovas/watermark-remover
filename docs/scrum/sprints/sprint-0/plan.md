# Sprint 0 — Fundación técnica

> Ver también: [Estimación del sprint](estimation.md) · [Definition of Done del sprint](definition_of_done.md) · [Product Backlog](../../product_backlog.md) · [DoD base](../../dod_base.md)

**Objetivo del sprint:** dejar el proyecto listo para empezar a construir funcionalidad: entorno de pruebas reproducible, validación de viabilidad del motor de IA local y de la integración barata con Claude.

## Alcance (historias)
- HU-1: Entorno de desarrollo y pruebas reproducible (Docker solo para tests)
- HU-2: Spike — validar motor de inpainting local (IOPaint/LaMa)
- HU-3: Spike — integración de bajo costo con Claude API

## Entregables esperados
- Repositorio con estructura base (`src/`, `tests/`, `docs/`, `docker/`).
- `docker-compose.yml` + `docker/Dockerfile.test` funcionando.
- Documento de resultados de los spikes (viabilidad, tiempos, costos) agregado a `docs/research/best_practices.md`.

## Fuera de alcance en Sprint 0
- UI final, selección múltiple real, empaquetado con PyInstaller (eso empieza en el Sprint 1, Épica 2).
