# Roles y ceremonias Scrum

> Ver también: [Product Backlog](product_backlog.md) · [Roadmap de sprints](roadmap.md) · [DoD base](dod_base.md)

Adaptado a un equipo pequeño (1-2 desarrolladores, ver supuesto de capacidad en [roadmap.md](roadmap.md)). Con equipos así de chicos, varios roles los cubre la misma persona — eso es válido en Scrum siempre que las responsabilidades queden claras y no se mezclen las decisiones (p. ej. quien prioriza el backlog no debería ser quien se autoexime de la Definition of Done).

## Roles

### Product Owner (PO)
- Dueño del [Product Backlog](product_backlog.md): prioriza historias, decide MoSCoW, acepta o rechaza el incremento al final de cada sprint.
- Responde preguntas de negocio/producto (ej. "¿el modo alta calidad con SD es prioridad ahora?").
- En equipo de 1-2 personas: normalmente el mismo dueño del proyecto/idea.

### Scrum Master
- Vela por que se sigan las ceremonias y el proceso (no por gestionar personas).
- Remueve impedimentos (ej. bloqueo técnico, falta de acceso a algo).
- Facilita retro y planning; protege al equipo de scope creep a mitad de sprint.
- En equipo de 1-2 personas: puede rotar o ser la misma persona que el equipo de desarrollo, pero **dedicando tiempo explícito** a este rol (no es "gratis" solo por ser pocos).

### Development Team
- Estima historias ([estimation.md](estimation.md)), desglosa tareas (ver `plan.md` de cada sprint), implementa, escribe tests, valida contra la Definition of Done.
- Autogestionado en el día a día: decide cómo implementar, no qué ni cuándo (eso es del PO/backlog).

### Claude Code (asistente de desarrollo)
- No es un rol Scrum formal, pero participa como apoyo al Development Team: ayuda a escribir código, documentar, revisar. Las decisiones de aceptación de historias siguen siendo humanas (PO/equipo).

## Ceremonias

| Ceremonia | Cuándo | Duración sugerida | Propósito |
|---|---|---|---|
| **Sprint Planning** | Primer día de cada sprint | 1-2h (sprint de 2 semanas) | Seleccionar historias del backlog para el sprint (ver [roadmap.md](roadmap.md)), confirmar que caben en la capacidad, y que cada una tiene su desglose de tareas en `sprints/sprint-N/plan.md`. |
| **Daily Standup** | Diario (o cada 2 días si el equipo es de 1 persona) | 5-15 min | ¿Qué hice? ¿Qué voy a hacer? ¿Qué me bloquea? Con equipo de 1 persona, esto se vuelve una nota corta de auto-seguimiento en vez de una reunión. |
| **Backlog Refinement** | A mitad de sprint (una vez) | 30-60 min | Revisar/ajustar historias futuras del [Product Backlog](product_backlog.md), re-estimar si hay nueva información (ej. resultado de un spike cambia el alcance de HU-7). |
| **Sprint Review** | Último día del sprint | 30-60 min | Demostrar el incremento funcionando (no solo código, sino la app corriendo) contra la [Definition of Done del sprint](roadmap.md). El PO acepta o rechaza cada historia. |
| **Sprint Retrospective** | Después del Review, mismo día | 30-45 min | Qué funcionó / qué no / qué cambiar para el próximo sprint. Se documenta como entrada nueva más abajo en este archivo (sección "Bitácora de retros"), para no perder el aprendizaje. |

## Cadencia recomendada para este proyecto
- Sprints de **2 semanas**, alineados con el [roadmap.md](roadmap.md) (Sprint 0 a Sprint 3).
- Sprint Review de cada sprint valida directamente contra la Definition of Done de ese sprint (`sprints/sprint-N/definition_of_done.md`).

## Bitácora de retros
_(se completa al final de cada sprint, con fecha y hallazgos — vacío hasta que arranque la ejecución)_

- Sprint 0: _pendiente_
- Sprint 1: _pendiente_
- Sprint 2: _pendiente_
- Sprint 3: _pendiente_
