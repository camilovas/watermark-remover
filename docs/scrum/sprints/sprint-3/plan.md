# Sprint 3 — Calidad y distribución

> Ver también: [Estimación del sprint](estimation.md) · [Definition of Done del sprint](definition_of_done.md) · [Roadmap](../../roadmap.md) · [Product Backlog](../../product_backlog.md)

**Objetivo del sprint:** cerrar el MVP para poder distribuirlo — empaquetado standalone probado en máquina limpia, y suite de pruebas endurecida.

## Alcance (historias) y desglose de tareas

### HU-9: Empaquetado como ejecutable standalone ✅ (con una limitación documentada)
- [x] Configurar comando de PyInstaller — los plugins de Qt (`qwindows`) se incluyen automáticamente vía el hook `pyi_rth_pyside6.py` de PyInstaller, sin configuración manual
- [x] Verificar assets: el MVP actual no tiene íconos/recursos propios que empaquetar (no hay `--add-data` que agregar); queda como mejora cosmética futura (ícono de la app)
- [x] Generar el `.exe` en el entorno de desarrollo y probarlo ahí — arranca y corre sin errores
- [x] Probar con un `PATH` mínimo simulando una máquina limpia (sin acceso a Python/IOPaint del sistema) — **la app arranca y funciona normalmente** (no se dispuso de una VM real en esta sesión, ver limitación abajo)
- [x] Documentar en README el paso a paso de build y troubleshooting
- [x] Tamaño del build: ~110MB — razonable, no requirió exclusiones adicionales

**Limitación real encontrada y documentada (no resuelta en este sprint):** el `.exe` empaqueta la UI y toda la lógica de la app, pero **no empaqueta IOPaint** — nuestro `IOPaintEngine` lo invoca como proceso CLI externo (`iopaint run`), no como librería Python importada, así que PyInstaller no puede detectarlo ni incluirlo automáticamente. Confirmado que esto **no crashea la app**: sin IOPaint instalado, todo funciona (cargar imágenes, marcar máscara) excepto "Procesar", que falla con un mensaje de error claro. Para una distribución real a un usuario final se necesita instalar IOPaint por separado (`pip install iopaint`, documentado en el README) — lo cual requiere Python en esa máquina solo para ese paso, contradiciendo parcialmente el objetivo original de "cero dependencias". Empaquetar IOPaint completo (incluye PyTorch) es significativamente más complejo/pesado y queda como trabajo futuro fuera del alcance de este sprint.

### HU-10: Suite de pruebas automatizadas (cierre/endurecimiento) ✅
- [x] Fixtures reutilizables consolidadas en `tests/conftest.py` (fixture `qapp` única a nivel de sesión, antes duplicada en 5 archivos; `sample_image_path`); se quitó el `sys.path.insert` repetido de cada archivo
- [x] Cobertura de tests para `core/` (`batch_processor`, `inpainting_engine`, `watermark_detector`) — `quality_checker` no se implementó: no es un criterio de aceptación comprometido en ninguna HU del backlog (solo aparecía como idea en el diseño de arquitectura), así que no se construyó sin que el producto lo pidiera
- [x] Cobertura de tests para `services/ollama_client` (`tests/test_ollama_client.py`, 7 tests, mockeando `requests.get`/`requests.post` — sin llamadas reales)
- [x] `pytest-cov` configurado en `pyproject.toml`: umbral **80%** sobre `core/`, `services/`, `utils/` (la UI se excluye del umbral — se verifica con pruebas funcionales end-to-end, no cobertura automatizada de interacción de mouse). Cobertura actual: **91.44%**
- [x] Suite corre igual en local y en Docker (`docker-compose up test` ahora incluye `--cov`)
- [x] Revisado: ningún test depende de red real ni de una instancia de Ollama real — todos los `OllamaClient`/detectores en tests usan `MagicMock` o `@patch` sobre `requests`

## Fuera de alcance en Sprint 3
- HU-11 (motor Stable Diffusion de alta calidad) — backlog futuro, post-MVP.
