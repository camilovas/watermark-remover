# Definition of Done — Sprint 3

> Ver también: [Plan del sprint](plan.md) · [Estimación del sprint](estimation.md) · [DoD base del proyecto](../../dod_base.md)

Extiende el [DoD base](../../dod_base.md) con el criterio de cierre de MVP:

1. HU-9 y HU-10 cumplen sus criterios de aceptación del [Product Backlog](../../product_backlog.md).
2. El `.exe` generado corre el flujo completo (cargar → marcar → procesar → lote → guardar) en una máquina Windows limpia, sin Python ni Docker instalados.
3. Cobertura de tests reportada (vía `pytest-cov`) y documentada; sin dependencias de red real en ningún test.
4. Todas las historias del MVP (HU-1 a HU-10) están en estado "Done" según sus respectivos DoD de sprint.
5. README y `CLAUDE.md` reflejan el estado real del producto (ya no "fase de planeación").
