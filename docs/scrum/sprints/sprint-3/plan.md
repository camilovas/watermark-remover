# Sprint 3 — Calidad y distribución

> Ver también: [Estimación del sprint](estimation.md) · [Definition of Done del sprint](definition_of_done.md) · [Roadmap](../../roadmap.md) · [Product Backlog](../../product_backlog.md)

**Objetivo del sprint:** cerrar el MVP para poder distribuirlo — empaquetado standalone probado en máquina limpia, y suite de pruebas endurecida.

## Alcance (historias) y desglose de tareas

### HU-9: Empaquetado como ejecutable standalone
- [ ] Configurar comando/spec de PyInstaller incluyendo plugins de Qt (`qwindows` en Windows)
- [ ] Verificar inclusión de assets (íconos, recursos) vía `--add-data`
- [ ] Generar el `.exe` en el entorno de desarrollo y probarlo ahí
- [ ] Probar el `.exe` en una VM/máquina limpia **sin Python ni Docker instalado**
- [ ] Documentar en README el paso a paso de build y troubleshooting de plugins de Qt
- [ ] Revisar tamaño del build y excluir librerías no usadas si es excesivo

### HU-10: Suite de pruebas automatizadas (cierre/endurecimiento)
- [ ] Revisar fixtures reutilizables (imágenes de prueba, `ImageItem` falso, mocks de engine/detector) usadas en sprints anteriores y consolidarlas
- [ ] Completar cobertura de tests para `core/` (`batch_processor`, `inpainting_engine`, `watermark_detector`, `quality_checker`)
- [ ] Completar cobertura de tests para `services/ollama_client` (mockeado, sin llamadas reales)
- [ ] Configurar medición de cobertura (`pytest-cov`) y definir un umbral mínimo razonable
- [ ] Confirmar que toda la suite corre igual en local (`pytest`) y en `docker-compose run test`
- [ ] Revisión final de que ningún test dependa de red real ni de una instancia de Ollama real sin mockear

## Fuera de alcance en Sprint 3
- HU-11 (motor Stable Diffusion de alta calidad) — backlog futuro, post-MVP.
