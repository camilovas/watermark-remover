# Definition of Done — Sprint 3

> Ver también: [Plan del sprint](plan.md) · [Estimación del sprint](estimation.md) · [DoD base del proyecto](../../dod_base.md)

Extiende el [DoD base](../../dod_base.md) con el criterio de cierre de MVP:

1. ✅ HU-9 y HU-10 cumplen sus criterios de aceptación del [Product Backlog](../../product_backlog.md) — HU-9 con una limitación real documentada (ver punto 2).
2. ⚠️ **Parcialmente cumplido, documentado con honestidad:** el `.exe` corre la UI completa (cargar → marcar máscara → lote → guardar) en una máquina Windows sin Python instalado — verificado con un `PATH` mínimo simulando una máquina limpia (no se dispuso de una VM real en esta sesión). El paso "procesar" específicamente **requiere que IOPaint esté instalado por separado** en la máquina destino (`pip install iopaint`, lo que sí requiere Python para ese único paso) — nuestro motor lo invoca como proceso CLI externo, no como librería empaquetable por PyInstaller. Sin IOPaint instalado, la app no crashea: muestra un error claro. Documentado en README y en `sprints/sprint-3/plan.md` como limitación conocida, no resuelta en este sprint.
3. ✅ Cobertura de tests: 91.44% (umbral configurado: 80%, sobre `core/`/`services/`/`utils/`) vía `pytest-cov`, reportada en `pyproject.toml`; cero dependencias de red real en los 41 tests (todo mockeado con `MagicMock`/`@patch`).
4. ✅ Los 4 sprints del MVP (HU-1 a HU-10) están en estado "Done" según sus respectivos DoD.
5. ✅ README y `CLAUDE.md` actualizados reflejando el estado real (app funcional, no "fase de planeación").

**Sprint 3 completado — con una limitación de alcance conocida y documentada (empaquetado de IOPaint), no un vacío silencioso.** Ver [research/best_practices.md](../../../research/best_practices.md) para el detalle técnico y posibles caminos futuros (bundlear IOPaint completo, o distribuir un instalador que lo resuelva en el primer arranque).
