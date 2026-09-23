# Estimación y priorización del Product Backlog

Escala: **Fibonacci** (1, 2, 3, 5, 8, 13) en story points, relativa a complejidad/esfuerzo/incertidumbre (no horas).
Prioridad: **MoSCoW** (Must / Should / Could / Won't-this-release).

| HU | Título | Épica | Story Points | Prioridad | Justificación breve |
|---|---|---|---:|---|---|
| HU-1 | Entorno de pruebas reproducible (Docker) | 1 — Base | 2 | Must | Config estándar (Dockerfile + compose), baja incertidumbre |
| HU-2 | Spike — validar IOPaint/LaMa local | 1 — Base | 3 | Must | Incertidumbre técnica (instalación, dependencias, tiempos) aunque sea "solo probar" |
| HU-3 | Spike — integración barata con Claude API | 1 — Base | 2 | Must | Llamada simple a API + medición de tokens |
| HU-4 | Selección múltiple de imágenes | 2 — Carga | 3 | Must | UI estándar de Qt (QFileDialog multi-select + drag&drop) |
| HU-5 | Marcado manual de región (mask editor) | 3 — Remoción | 5 | Must | Requiere manejo de eventos de mouse/canvas, redimensionar/mover; es el corazón de la UX |
| HU-6 | Sugerencia automática de región vía Claude | 3 — Remoción | 5 | Should | Depende de HU-3 y HU-5; maneja ausencia de API key y feedback visual de la sugerencia |
| HU-7 | Procesamiento de imagen (inpainting local) | 3 — Remoción | 8 | Must | Integración con IOPaint, manejo de errores, formatos, calidad de resultado |
| HU-8 | Procesamiento por lotes (progreso + cancelar) | 3 — Remoción | 8 | Must | Concurrencia (QThread), cancelación segura, manejo de errores parciales |
| HU-9 | Empaquetado como ejecutable standalone | 4 — Distribución | 5 | Must | PyInstaller + plugins Qt + prueba en máquina limpia; puede requerir iteración |
| HU-10 | Suite de pruebas automatizadas | 5 — Calidad | 5 | Must | Mocks de engine/detector, corre local y en Docker |
| HU-11 | Motor alternativo alta calidad (Stable Diffusion) | 3 — Remoción (futuro) | 13 | Won't (fuera del MVP) | Alta incertidumbre, requiere detección de GPU, mucho más pesado |

## Totales
- **Total MVP (Must + Should, sin HU-11):** 2+3+2+3+5+5+8+8+5+5 = **46 story points**
- **Backlog futuro (Won't esta release):** HU-11 = 13 puntos, se revisa después del MVP.

## Dependencias relevantes para el roadmap
- HU-2 y HU-3 (spikes) deben ir antes de HU-6 y HU-7, ya que validan la viabilidad técnica de ambos motores.
- HU-5 (mask manual) es prerequisito de HU-6 (sugerencia automática solo la complementa) y de HU-7 (procesar necesita una máscara, manual o sugerida).
- HU-7 es prerequisito de HU-8 (el lote reutiliza el procesamiento individual).
- HU-9 (empaquetado) depende de tener HU-4, HU-5, HU-7, HU-8 funcionando (flujo completo a empaquetar).
- HU-10 (tests) se construye en paralelo a cada historia, no al final — cada HU de código debe traer sus tests (ver [Definition of Done](definition_of_done.md)).
