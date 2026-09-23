# Definition of Done — Sprint 0

> Ver también: [Plan del sprint](plan.md) · [Estimación del sprint](estimation.md) · [DoD base del proyecto](../../dod_base.md)

Sprint 0 es fundación técnica (entorno + spikes), no entrega funcionalidad de producto, así que su DoD ajusta la [base del proyecto](../../dod_base.md) a ese contexto:

1. `docker-compose up test` construye y corre la suite de pruebas sin errores (HU-1).
2. Se probó IOPaint/LaMa localmente procesando al menos una imagen de prueba con marca de agua, sin conexión a internet tras la descarga inicial del modelo (HU-2).
3. Se hizo al menos una llamada real a la API de Claude (miniatura) y se documentó el costo/tokens observado (HU-3).
4. Resultados de ambos spikes (HU-2, HU-3) documentados en [docs/research/best_practices.md](../../../research/best_practices.md), no solo mencionados de palabra.
5. Ningún secreto (API key) commiteado al repositorio (se usó variable de entorno o `.env` ignorado por git).
6. README actualizado si cambió algún comando de setup.

**No aplica en este sprint** (a diferencia del DoD base): criterios de aceptación de UI, empaquetado con PyInstaller, o pruebas sobre código de producto — porque Sprint 0 no produce ese código todavía.
