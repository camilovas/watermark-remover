# Investigación: mejores prácticas

> Ver también: [Product Backlog](../scrum/product_backlog.md) · [Arquitectura](../architecture/overview.md)

Investigación realizada en Sprint 0 para fundamentar decisiones de arquitectura. Cada hallazgo se traduce en criterios de aceptación dentro del [Product Backlog](../scrum/product_backlog.md).

## 1. Motor de remoción de marcas de agua (IA local)

- **LaMa** (Large Mask Inpainting): modelo ligero, eficiente en CPU/GPU modesta, referencia estándar para inpainting de objetos y marcas de agua.
- **IOPaint**: herramienta open-source que envuelve LaMa (y otros modelos como Stable Diffusion) con servidor local, CLI y API HTTP. Activamente mantenida, soporta procesamiento por lotes. Buen candidato para el MVP porque expone una API local que la app de escritorio puede consumir sin depender de internet.
- **WatermarkRemover-AI** (Florence-2 + LaMa): combina un modelo de detección de región (Florence-2) con LaMa para reconstrucción. Confirma el patrón "detectar región → inpaint" como el más usado en proyectos open-source similares.

**Decisión de arquitectura derivada:** usar **IOPaint (LaMa) local** como motor de inpainting (gratis, offline, sin costo por imagen). La detección de la región de marca de agua se apoya opcionalmente en **Ollama** (modelo de visión local, ej. `moondream`), corriendo en esta máquina o en otra de la misma red — reservando el cómputo pesado (generación de píxeles) para el modelo local de inpainting.

### Hallazgos del spike HU-2 (IOPaint/LaMa, instalado y probado localmente, fuera de Docker)
- Instalación: `pip install iopaint` (v1.6.0) funcionó sin problemas en Python 3.10 local (Windows). Nota: baja `Pillow` a 9.5.0 (fijado por iopaint), lo cual puede chocar con otras herramientas del sistema que pidan Pillow más reciente — dentro del entorno virtual propio del proyecto esto no es un problema.
- CLI: `iopaint run --model lama --device cpu --image <img> --mask <mask> --output <dir>`.
- **Primera corrida** (incluye descarga del modelo `big-lama.pt`): 144s.
- **Corridas siguientes** (modelo ya cacheado en `~/.cache/torch/hub/checkpoints/`): **~25s totales, de los cuales solo ~7s son inferencia pura** — el resto es overhead de cargar el modelo a memoria. Medido en CPU, sin GPU, sobre una imagen de 1200×800px.
- **Calidad del resultado**: sobre la imagen de prueba sintética, LaMa eliminó completamente el texto de la marca de agua y reconstruyó el patrón de fondo (rayas verticales) de forma convincente. Se observó un artefacto leve (línea tenue) en el borde de la máscara — aceptable para el caso de uso, pero sugiere que ajustar la máscara con un poco de margen/difuminado alrededor de la marca de agua real mejoraría el resultado (tarea para HU-5: el mask editor podría ofrecer un "grow/feather" configurable).
- **Conclusión:** IOPaint/LaMa es viable como motor por defecto: rápido en CPU (unos segundos por imagen), sin necesitar GPU, y con buena calidad visual para el caso de uso principal. Corre completamente offline una vez descargado el modelo (~200MB, una sola vez).

Fuentes:
- [lama-inpainting · GitHub Topics](https://github.com/topics/lama-inpainting)
- [IOPaint - Free and Open-Source AI Image Inpainting Tool](https://aibars.net/en/projects/725043813751590912)
- [WatermarkRemover-AI](https://www.scriptbyai.com/watermark-detection-removal/)

## 1.1 Modelo de Deep Learning / Machine Learning: costo vs calidad

Comparación de las opciones de motor de inpainting (deep learning) pensando en minimizar costo sin sacrificar calidad:

| Modelo | Tipo | Params | Requiere GPU | Costo | Calidad |
|---|---|---|---|---|---|
| **LaMa** | CNN generativa (GAN), un solo paso | ~27M | No (corre bien en CPU) | $0 — corre local | Buena para regiones regulares tipo marca de agua/logo; menor fidelidad que difusión en fondos muy complejos/texturizados |
| **Stable Diffusion inpainting** (vía IOPaint) | Difusión | >800M | Recomendado (lento en CPU) | $0 pero cómputo pesado (tiempo/energía) o costo de GPU en la nube | Mayor fidelidad y coherencia semántica, pero mucho más lento y pesado |

**Conclusión:** LaMa es la opción que mejor equilibra costo (gratis, corre en CPU de cualquier PC, sin depender de GPU) y calidad suficiente para el caso de uso principal (logos/marcas de agua, que son regiones relativamente regulares). Se deja como **mejora futura opcional** (backlog, no MVP) un "modo alta calidad" con Stable Diffusion para el usuario que tenga GPU y prefiera priorizar calidad sobre velocidad.

### Rol de Ollama (pivote de arquitectura, ver Sprint 0)
El plan original consideraba la API de Claude (pago por token) para la detección/QC. Se decidió reemplazarla por **Ollama** corriendo un modelo de visión local (`moondream`, ~1.7GB, liviano) porque:
- **Costo $0**: no hay cobro por token ni por llamada, solo el cómputo de la máquina que corre Ollama.
- **Sin API key ni internet**: coherente con el requisito de que la app funcione en cualquier PC sin depender de un servicio externo.
- **Corre en red local**: Ollama expone su API HTTP (`http://<host>:11434` por defecto) — puede correr en la misma máquina del usuario, o en **otra máquina de la red local** que sí tenga el modelo cargado (ej. un equipo más potente compartido por varios usuarios). La app debe permitir configurar el host de Ollama (`OLLAMA_HOST`), no asumir siempre `localhost`.
- **Modelo elegido (`moondream`)**: liviano y rápido, suficiente para una tarea simple como devolver un bounding box sobre una miniatura reducida (~512px). Si se necesita más precisión, `llava:7b` es una alternativa más pesada.

### Hallazgos del spike HU-3

**1. Causa raíz real: bug de GPU/Vulkan en Ollama, no del modelo.**
Al llamar `POST /api/generate` (imagen de prueba sintética `tests/fixtures/sample_watermarked.png`, miniatura ~512px), Ollama devolvía consistentemente un error 500:
```
llama-server process has terminated: exit status 0xc0000409:
The system detected an overrun of a stack-based buffer in this application.
```
El log de Ollama (`%LOCALAPPDATA%\Ollama\server.log`) mostró la causa real: `ERROR: vkQueueSubmit: Invalid queue [VUID-vkQueueSubmit-queue-parameter]` — un fallo del backend Vulkan al intentar descargar capas del modelo a la GPU. **Esto no era específico de `moondream`**: el mismo crash ocurría con `llava:7b` e incluso con `qwen2.5-coder:7b` (modelo de solo texto, sin visión), confirmando que es un problema de GPU/drivers en esta máquina, no de compatibilidad de un modelo puntual. Persistió igual tras actualizar Ollama 0.34.1 → 0.34.3.

**Solución:** forzar inferencia en CPU pasando `"options": {"num_gpu": 0}` en cada request. Con eso, tanto `moondream` como `llava:7b` y `qwen2.5-coder:7b` funcionan sin crashear.

**2. Comparación de modelos en CPU (mismo prompt, misma miniatura):**

| Modelo | Tiempo respuesta | Resultado | Nota |
|---|---|---|---|
| `moondream` (1.7GB) | ~51s | Devolvió un bounding box `[0.24, 0.68, 0.83, 0.87]` (normalizado 0-1, no en píxeles como se pidió) | Region detectada no coincide bien con la real (marca real en la esquina inferior derecha; detección más centrada) — precisión baja en esta prueba |
| `llava:7b` (4.7GB) | ~171s (2.85 min) | `{"found": false}` — no detectó la marca de agua presente | Más lento y con falso negativo en esta prueba |

**Decisión:** usar `moondream` como modelo por defecto (es ~3.4x más rápido que `llava:7b` en CPU y más liviano en disco), pero **forzando `num_gpu: 0`** hasta resolver el bug de Vulkan, y dejando el modelo configurable (no hardcodeado) para que el usuario pueda cambiarlo si tiene mejor GPU/drivers o prefiere `llava` por precisión.

**3. Riesgo de UX detectado:** 51-171 segundos por detección es lento para una función que se presenta como "automática" — HU-6 debe manejar esto con un indicador de progreso claro y no bloquear la UI (ya contemplado en el diseño con la interfaz `WatermarkDetector` async). La precisión también fue baja en esta prueba sintética; se recomienda ajustar el prompt y probar con imágenes reales (no sintéticas) antes de confiar en la sugerencia automática sin que el usuario la revise — el diseño ya contempla esto (AC2 de HU-6: el usuario siempre puede ajustar/rechazar la sugerencia).

Fuentes:
- [Best Open-Source Image Generation Models (2026) — Thunder Compute](https://www.thundercompute.com/blog/best-open-source-image-generation-models)
- [Inpainting runtime decision doc](https://github.com/SysAdminDoc/Images/blob/main/docs/inpaint-runtime-decision.md)
- [Ollama — documentación oficial](https://github.com/ollama/ollama)

## 2. Empaquetado de app de escritorio (PySide6/PyQt6 + PyInstaller)

- Usar **PySide6** (licencia LGPL, sin costo de licenciamiento comercial como PyQt6 en algunos casos) + **PyInstaller** actualizado.
- Cuidado con los **plugins de plataforma de Qt** (`qwindows` en Windows, `xcb` en Linux, `qcocoa` en macOS): deben empaquetarse explícitamente o el ejecutable no arranca.
- Preferir `pyside6-deploy` quie sobre PyInstaller manual cuando sea posible, para un ejecutable más optimizado.
- Trabajar siempre dentro de un entorno virtual y apuntar `--add-data` a rutas dentro de ese entorno.

**Decisión derivada:** el ejecutable final (.exe) debe funcionar en cualquier PC Windows sin Docker ni Python preinstalado. Docker/docker-compose se usan **solo** para entornos de prueba reproducibles (tests automatizados, servidor IOPaint de referencia en CI), nunca como requisito de distribución.

### Hallazgo del spike/build HU-9: el .exe no incluye IOPaint

Al empaquetar con PyInstaller (`--windowed --paths src`), el build funcionó **mejor de lo esperado** en un aspecto: los plugins de Qt (`qwindows`) se incluyen automáticamente gracias al hook `pyi_rth_pyside6.py` que trae PyInstaller de fábrica — el riesgo anticipado en el roadmap ("si HU-9 encuentra problemas de plugins de Qt, puede consumir más de un sprint") no se materializó.

Sí apareció un hallazgo real distinto: **el `.exe` (~110MB) no incluye IOPaint**. Nuestro `IOPaintEngine` invoca IOPaint como proceso externo (`subprocess.run(["iopaint", "run", ...])`), nunca como `import iopaint` — así que PyInstaller, que solo empaqueta lo que el código Python importa, no tiene forma de detectarlo ni incluirlo automáticamente.

- **Verificado que no rompe la app:** se lanzó el `.exe` con un `PATH` mínimo (simulando una máquina limpia sin Python/IOPaint) y la aplicación arranca y funciona normalmente — cargar imágenes, marcar máscara, todo funciona. Solo el botón "Procesar" falla, con un mensaje de error claro (`InpaintingEngineError`), no un crash.
- **Implicación para distribución real:** el usuario final necesita `pip install iopaint` una vez en su máquina antes de poder usar la función principal de la app — lo cual requiere Python instalado solo para ese paso, en tensión con el objetivo original de "cero dependencias".
- **Por qué no se resolvió en este sprint:** empaquetar IOPaint completo implica bundlear PyTorch (y sus decenas de dependencias, varios GB), algo significativamente más complejo que el resto del empaquetado y con retos propios de PyInstaller (hooks para librerías científicas, tamaño del ejecutable). Se documenta como **trabajo futuro** con dos caminos posibles:
  1. Bundlear un entorno Python portable con IOPaint preinstalado junto al `.exe` (carpeta `_internal` más grande, pero sigue siendo "un solo paquete que copiar").
  2. Un instalador (ej. Inno Setup) que en el primer arranque descargue/instale IOPaint automáticamente, sin requerir que el usuario abra una terminal.

Fuentes:
- [Packaging PySide6 and PyQt6 Apps with PyInstaller](https://www.pythonguis.com/faq/pyinstaller-4-2-pyside6/)
- [Deployment - Qt for Python](https://doc.qt.io/qtforpython-6/deployment/index.html)

## 3. Scrum aplicado a un proyecto pequeño

- Sprint 0 dedicado a spikes técnicos (validar IOPaint local, validar llamada a Ollama) antes de comprometer historias de producto.
- Historias de usuario con formato `Como... quiero... para...` + criterios de aceptación verificables (Given/When/Then), derivados de esta investigación.
- Definition of Done explícita que incluya: pruebas automatizadas corriendo en Docker, funcionamiento del .exe sin Docker, revisión de código.

## Criterios de aceptación generales derivados de esta investigación

1. La app debe ejecutar el motor de inpainting **sin conexión a internet** y sin Docker instalado en la máquina del usuario final.
2. Docker y docker-compose se usan exclusivamente para levantar el entorno de pruebas (tests unitarios/integración, y opcionalmente un IOPaint de referencia); no deben ser una dependencia para ejecutar la app empaquetada.
3. Las llamadas a Ollama deben limitarse a tareas livianas (ej. detección de región sobre una miniatura, no el procesamiento de la imagen completa) y deben ser opcionales/activables (la app debe poder operar 100% local/manual si Ollama no está disponible).
4. El empaquetado con PyInstaller debe incluir explícitamente los plugins de plataforma de Qt necesarios y probarse en una máquina limpia (sin Python) antes de cerrar cualquier historia de "release".
5. La selección múltiple de imágenes y el procesamiento por lotes deben mostrar progreso y permitir cancelar.
6. Las llamadas a Ollama deben usar el modelo de visión más liviano que cumpla la tarea (`moondream` por defecto) sobre miniaturas reducidas (~512px), no un modelo más pesado, salvo que el usuario lo configure explícitamente.
7. El motor local por defecto debe ser LaMa (CPU-friendly, sin costo); un motor basado en difusión (mayor calidad, mayor costo computacional) queda como mejora opcional futura, no como requisito del MVP.
