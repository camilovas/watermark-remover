# Quitar Marca de Agua — contexto del proyecto

App de escritorio (Python + PySide6) para eliminar marcas de agua de imágenes con IA, con selección múltiple/lotes. Metodología **Scrum**. Debe funcionar en cualquier PC **sin Docker**; Docker/docker-compose se usan **solo** para pruebas. Motor de IA local (LaMa/IOPaint) hace el trabajo pesado; Claude (modelo Haiku, sobre miniaturas) asiste en tareas baratas y opcionales (detección de región, control de calidad).

Estado actual: **fase de planeación** (Sprint 0 aún no ejecutado — ver [docs/scrum/sprints/sprint-0/plan.md](docs/scrum/sprints/sprint-0/plan.md)). No hay código de la app todavía, solo documentación y esqueleto de repo.

## Mapa de documentación

| Carpeta | Contenido | Documentos |
|---|---|---|
| `docs/research/` | Investigación y mejores prácticas que fundamentan las decisiones | [best_practices.md](docs/research/best_practices.md) |
| `docs/architecture/` | Diseño técnico | [overview.md](docs/architecture/overview.md) (visión general), [detailed.md](docs/architecture/detailed.md) (módulos, interfaces, diagramas) |
| `docs/scrum/` | Artefactos ágiles a nivel de producto | [product_backlog.md](docs/scrum/product_backlog.md) (épicas/historias/criterios de aceptación), [estimation.md](docs/scrum/estimation.md) (story points de TODO el backlog), [dod_base.md](docs/scrum/dod_base.md) (mínimo común, heredado por cada sprint) |
| `docs/scrum/sprints/` | Un subfolder por sprint (`sprint-0/`, `sprint-1/`, ...), cada uno con **su propio** `plan.md`, `estimation.md` (subset del backlog) y `definition_of_done.md` (hereda `dod_base.md` + criterios propios) | [sprint-0/](docs/scrum/sprints/sprint-0/) |

## Cómo se conectan
- **Backlog** (`product_backlog.md`) es la fuente de verdad de las historias (HU-1 a HU-11); sus criterios de aceptación derivan de `research/best_practices.md`.
- **Estimation** general (`estimation.md`) asigna story points/prioridad/dependencias a cada HU del backlog completo — úsalo junto al backlog, no por separado.
- **Architecture** (`overview.md` + `detailed.md`) traduce las historias en diseño técnico (módulos, interfaces Strategy/Null Object, diagramas de flujo).
- Cada **sprint** (`sprints/sprint-N/`) recorta un subconjunto de historias del backlog y trae su propia `estimation.md` (solo esas historias) y `definition_of_done.md` (hereda `dod_base.md` + ajustes propios del sprint, ej. un sprint de spikes no exige empaquetado). Sprint 0 = HU-1, HU-2, HU-3.
- **`dod_base.md`** es el mínimo común a todos los sprints; nunca se relaja, solo se extiende por sprint.

## Convenciones de este repo
- Toda decisión de arquitectura debe quedar justificada en `docs/research/` antes (o al momento) de escribirse en `docs/architecture/`.
- Cada HU nueva se agrega al backlog con AC (criterios de aceptación) y luego se estima en `estimation.md`.
- Docker/docker-compose (`docker-compose.yml`, `docker/Dockerfile.test`) son **solo** para pruebas — nunca dependencia de distribución (ver HU-1 y arquitectura).
- Commits en español, formato imperativo, siguiendo el estilo ya usado en el historial de este repo.
