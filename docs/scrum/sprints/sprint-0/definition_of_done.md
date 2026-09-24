# Definition of Done — Sprint 0

> Ver también: [Plan del sprint](plan.md) · [Estimación del sprint](estimation.md) · [DoD base del proyecto](../../dod_base.md)

Sprint 0 es fundación técnica (entorno + spikes), no entrega funcionalidad de producto, así que su DoD ajusta la [base del proyecto](../../dod_base.md) a ese contexto:

1. ✅ `docker-compose up test` construye y corre la suite de pruebas sin errores (HU-1) — verificado, 1 test passed.
2. ✅ Se probó IOPaint/LaMa localmente procesando una imagen de prueba con marca de agua (HU-2) — ~7s de inferencia en CPU, resultado visualmente correcto, modelo cacheado localmente tras la primera descarga.
3. ✅ Se hizo una llamada real a Ollama (miniatura) y se documentó el tiempo de respuesta observado (HU-3) — con hallazgo relevante: bug de GPU/Vulkan resuelto forzando `num_gpu: 0`.
4. ✅ Resultados de ambos spikes (HU-2, HU-3) documentados en [docs/research/best_practices.md](../../../research/best_practices.md).
5. ✅ Ningún dato sensible commiteado al repositorio.
6. ✅ README actualizado (sección de Ollama con el nuevo flujo de configuración).

**Sprint 0: completado.** Los tres spikes (HU-1, HU-2, HU-3) están resueltos y documentados. Listo para arrancar Sprint 1.

**No aplica en este sprint** (a diferencia del DoD base): criterios de aceptación de UI, empaquetado con PyInstaller, o pruebas sobre código de producto — porque Sprint 0 no produce ese código todavía.
