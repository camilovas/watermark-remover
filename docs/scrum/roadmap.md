# Roadmap de Sprints

> Ver también: [Product Backlog](product_backlog.md) · [Estimación general](estimation.md) · [DoD base](dod_base.md) · [Roles y ceremonias](roles_ceremonies.md)

**Supuesto de capacidad** (ajustable): equipo pequeño (1-2 desarrolladores), sprints de 2 semanas, velocidad estimada ~15 story points/sprint. Si el equipo real es distinto, recalcular la distribución de historias por sprint — las dependencias documentadas en [estimation.md](estimation.md#dependencias-relevantes-para-el-roadmap) no cambian.

## Vista general

| Sprint | Objetivo | Historias | Story Points |
|---|---|---|---:|
| [Sprint 0](sprints/sprint-0/) | Fundación técnica: entorno de pruebas + validar viabilidad de motor local y de Claude | HU-1, HU-2, HU-3 | 7 |
| [Sprint 1](sprints/sprint-1/) | Flujo end-to-end de una sola imagen: cargar, marcar máscara, procesar local | HU-4, HU-5, HU-7 | 16 |
| [Sprint 2](sprints/sprint-2/) | Escalar a lotes + asistencia opcional de Claude | HU-6, HU-8 | 13 |
| [Sprint 3](sprints/sprint-3/) | Cierre de calidad y distribución | HU-9, HU-10 | 10 |

**Total MVP: 46 puntos en 4 sprints** (~11.5 pts/sprint en promedio, razonable considerando que Sprint 0 es más liviano por ser fundación).

Fuera del roadmap del MVP: **HU-11** (motor Stable Diffusion de alta calidad, 13 pts) — se revisa en un sprint posterior, después de validar el MVP con usuarios reales.

## Por qué este orden (dependencias)
1. **Sprint 0** valida que ambos motores (IOPaint local y Claude API) son viables antes de comprometer diseño sobre ellos.
2. **Sprint 1** entrega lo mínimo para que el producto tenga valor real (una imagen, de principio a fin, sin necesitar Claude) — es el primer incremento demostrable.
3. **Sprint 2** agrega lo que multiplica el valor (lotes) y la mejora opcional de UX (detección automática), ambas construidas sobre lo ya probado en Sprint 1.
4. **Sprint 3** cierra con lo que no bloquea la demo pero sí el release real: empaquetado standalone y endurecimiento de la suite de pruebas.

## Riesgos que pueden mover fechas
- Si HU-2 (spike IOPaint) revela problemas de rendimiento en CPU, HU-7 podría crecer en Sprint 1 (impacto: mover HU-7 solo a Sprint 2 y dejar Sprint 1 con HU-4+HU-5).
- Si HU-9 (empaquetado) encuentra problemas de plugins de Qt, puede consumir más de un sprint — está aislada al final (Sprint 3) para no bloquear el resto.
