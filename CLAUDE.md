# Quitar Marca de Agua — contexto del proyecto

App de escritorio (Python + PySide6) para eliminar marcas de agua de imágenes con IA, con selección múltiple/lotes. Metodología **Scrum**. Debe funcionar en cualquier PC **sin Docker**; Docker/docker-compose se usan **solo** para pruebas. Motor de IA local (LaMa/IOPaint) hace el trabajo pesado; **Ollama** (modelo de visión local, ej. `moondream`, corriendo en esta máquina o en otra de la red) asiste en tareas livianas y opcionales (detección de región, control de calidad). Claude (aquí, Claude Code) es solo el asistente de desarrollo — no forma parte del producto final.

Estado actual: **Sprint 1 completado** (Sprint 0 y Sprint 1 ✅, ver [docs/scrum/roadmap.md](docs/scrum/roadmap.md)). Ya existe código funcional en `src/watermark_remover/`: flujo completo de una imagen (cargar → marcar máscara → procesar con IOPaint/LaMa local → comparar antes/después → guardar). Próximo: Sprint 2 (lotes + Ollama opcional).

## Mapa de documentación

| Carpeta | Contenido | Documentos |
|---|---|---|
| `docs/research/` | Investigación y mejores prácticas que fundamentan las decisiones | [best_practices.md](docs/research/best_practices.md) |
| `docs/architecture/` | Diseño técnico | [overview.md](docs/architecture/overview.md) (visión general), [detailed.md](docs/architecture/detailed.md) (módulos, interfaces, diagramas) |
| `docs/scrum/` | Artefactos ágiles a nivel de producto | [product_backlog.md](docs/scrum/product_backlog.md) (épicas/historias/criterios de aceptación), [estimation.md](docs/scrum/estimation.md) (story points de TODO el backlog), [dod_base.md](docs/scrum/dod_base.md) (mínimo común, heredado por cada sprint), [roles_ceremonies.md](docs/scrum/roles_ceremonies.md) (PO/Scrum Master/Dev Team, ceremonias) |
| `docs/scrum/sprints/` | Un subfolder por sprint (`sprint-0/` a `sprint-3/`), cada uno con **su propio** `plan.md` (con tareas desglosadas por historia), `estimation.md` (subset del backlog) y `definition_of_done.md` (hereda `dod_base.md` + criterios propios) | [roadmap.md](docs/scrum/roadmap.md) (vista general) · [sprint-0/](docs/scrum/sprints/sprint-0/) · [sprint-1/](docs/scrum/sprints/sprint-1/) · [sprint-2/](docs/scrum/sprints/sprint-2/) · [sprint-3/](docs/scrum/sprints/sprint-3/) |
| `src/watermark_remover/` | Código de la app (PySide6) | `ui/` (MainWindow, ImageListWidget, PreviewCanvas, MaskEditor), `core/` (ImageItem, InpaintingEngine/IOPaintEngine), `utils/` (image_utils, file_utils) — ver [architecture/detailed.md](docs/architecture/detailed.md) para el diseño completo |

## Cómo se conectan
- **Backlog** (`product_backlog.md`) es la fuente de verdad de las historias (HU-1 a HU-11); sus criterios de aceptación derivan de `research/best_practices.md`.
- **Estimation** general (`estimation.md`) asigna story points/prioridad/dependencias a cada HU del backlog completo — úsalo junto al backlog, no por separado.
- **Architecture** (`overview.md` + `detailed.md`) traduce las historias en diseño técnico (módulos, interfaces Strategy/Null Object, diagramas de flujo).
- El **roadmap** (`roadmap.md`) reparte todo el backlog del MVP en 4 sprints según dependencias: Sprint 0 = HU-1,2,3 (fundación) · Sprint 1 = HU-4,5,7 (flujo de una imagen) · Sprint 2 = HU-6,8 (lotes + Ollama opcional) · Sprint 3 = HU-9,10 (empaquetado + cierre de calidad).
- Cada **sprint** (`sprints/sprint-N/`) trae su propio `plan.md` (con tareas desglosadas por historia), `estimation.md` (solo sus historias) y `definition_of_done.md` (hereda `dod_base.md` + ajustes propios del sprint, ej. un sprint de spikes no exige empaquetado).
- **`dod_base.md`** es el mínimo común a todos los sprints; nunca se relaja, solo se extiende por sprint.

## Convenciones de este repo
- Toda decisión de arquitectura debe quedar justificada en `docs/research/` antes (o al momento) de escribirse en `docs/architecture/`.
- Cada HU nueva se agrega al backlog con AC (criterios de aceptación) y luego se estima en `estimation.md`.
- Docker/docker-compose (`docker-compose.yml`, `docker/Dockerfile.test`) son **solo** para pruebas — nunca dependencia de distribución (ver HU-1 y arquitectura).
- Commits en español, formato imperativo, siguiendo el estilo ya usado en el historial de este repo.
