# Investigación: mejores prácticas

> Ver también: [Product Backlog](../scrum/product_backlog.md) · [Arquitectura](../architecture/overview.md)

Investigación realizada en Sprint 0 para fundamentar decisiones de arquitectura. Cada hallazgo se traduce en criterios de aceptación dentro del [Product Backlog](../scrum/product_backlog.md).

## 1. Motor de remoción de marcas de agua (IA local)

- **LaMa** (Large Mask Inpainting): modelo ligero, eficiente en CPU/GPU modesta, referencia estándar para inpainting de objetos y marcas de agua.
- **IOPaint**: herramienta open-source que envuelve LaMa (y otros modelos como Stable Diffusion) con servidor local, CLI y API HTTP. Activamente mantenida, soporta procesamiento por lotes. Buen candidato para el MVP porque expone una API local que la app de escritorio puede consumir sin depender de internet.
- **WatermarkRemover-AI** (Florence-2 + LaMa): combina un modelo de detección de región (Florence-2) con LaMa para reconstrucción. Confirma el patrón "detectar región → inpaint" como el más usado en proyectos open-source similares.

**Decisión de arquitectura derivada:** usar **IOPaint (LaMa) local** como motor de inpainting (gratis, offline, sin costo por imagen). La detección de la región de marca de agua se apoya opcionalmente en **Claude Vision API** (tarea barata en tokens: analizar una miniatura y devolver coordenadas del bounding box), reservando el cómputo pesado (generación de píxeles) para el modelo local.

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

### Rol de Claude en el costo total
- Los modelos de Claude cobran por tokens; una imagen de referencia de 1000×1000 px equivale a ~1334 tokens de entrada. Con **Claude Haiku** (el modelo más económico, ~US$1 por millón de tokens de entrada), una llamada de detección de región sobre una miniatura (no la imagen completa) cuesta fracciones de centavo por imagen.
- **Decisión de costo:** usar **Claude Haiku** (no Sonnet/Opus) para las tareas de detección de región y control de calidad, ya que no requieren razonamiento complejo — solo visión sobre una miniatura reducida. Esto mantiene el costo por imagen prácticamente despreciable, cumpliendo el objetivo de "que Claude haga lo caro-de-hacer-localmente pero barato en tokens, y que el mayor esfuerzo lo haga el modelo local".
- Reducir siempre la imagen a una miniatura (ej. 512px de lado mayor) antes de enviarla a Claude, tanto para bajar tokens/costo como latencia.

Fuentes:
- [Best Open-Source Image Generation Models (2026) — Thunder Compute](https://www.thundercompute.com/blog/best-open-source-image-generation-models)
- [Inpainting runtime decision doc](https://github.com/SysAdminDoc/Images/blob/main/docs/inpaint-runtime-decision.md)
- [Vision API Cost Per Image: 2026 Pricing Compared](https://tokencost.app/blog/vision-api-cost-per-image)
- [Claude API Pricing Breakdown (2026)](https://nicolalazzari.ai/articles/claude-api-pricing-breakdown-2026)

## 2. Empaquetado de app de escritorio (PySide6/PyQt6 + PyInstaller)

- Usar **PySide6** (licencia LGPL, sin costo de licenciamiento comercial como PyQt6 en algunos casos) + **PyInstaller** actualizado.
- Cuidado con los **plugins de plataforma de Qt** (`qwindows` en Windows, `xcb` en Linux, `qcocoa` en macOS): deben empaquetarse explícitamente o el ejecutable no arranca.
- Preferir `pyside6-deploy` quie sobre PyInstaller manual cuando sea posible, para un ejecutable más optimizado.
- Trabajar siempre dentro de un entorno virtual y apuntar `--add-data` a rutas dentro de ese entorno.

**Decisión derivada:** el ejecutable final (.exe) debe funcionar en cualquier PC Windows sin Docker ni Python preinstalado. Docker/docker-compose se usan **solo** para entornos de prueba reproducibles (tests automatizados, servidor IOPaint de referencia en CI), nunca como requisito de distribución.

Fuentes:
- [Packaging PySide6 and PyQt6 Apps with PyInstaller](https://www.pythonguis.com/faq/pyinstaller-4-2-pyside6/)
- [Deployment - Qt for Python](https://doc.qt.io/qtforpython-6/deployment/index.html)

## 3. Scrum aplicado a un proyecto pequeño

- Sprint 0 dedicado a spikes técnicos (validar IOPaint local, validar llamada a Claude API) antes de comprometer historias de producto.
- Historias de usuario con formato `Como... quiero... para...` + criterios de aceptación verificables (Given/When/Then), derivados de esta investigación.
- Definition of Done explícita que incluya: pruebas automatizadas corriendo en Docker, funcionamiento del .exe sin Docker, revisión de código.

## Criterios de aceptación generales derivados de esta investigación

1. La app debe ejecutar el motor de inpainting **sin conexión a internet** y sin Docker instalado en la máquina del usuario final.
2. Docker y docker-compose se usan exclusivamente para levantar el entorno de pruebas (tests unitarios/integración, y opcionalmente un IOPaint de referencia); no deben ser una dependencia para ejecutar la app empaquetada.
3. Las llamadas a la API de Claude deben limitarse a tareas de bajo consumo de tokens (ej. detección de región sobre miniatura, no el procesamiento de la imagen completa) y deben ser opcionales/activables (la app debe poder operar 100% local si el usuario no configura una API key).
4. El empaquetado con PyInstaller debe incluir explícitamente los plugins de plataforma de Qt necesarios y probarse en una máquina limpia (sin Python) antes de cerrar cualquier historia de "release".
5. La selección múltiple de imágenes y el procesamiento por lotes deben mostrar progreso y permitir cancelar.
6. Las llamadas a Claude deben usar el modelo más económico que cumpla la tarea (Claude Haiku) sobre miniaturas reducidas (~512px), nunca un modelo más caro (Sonnet/Opus) para detección o control de calidad rutinarios.
7. El motor local por defecto debe ser LaMa (CPU-friendly, sin costo); un motor basado en difusión (mayor calidad, mayor costo computacional) queda como mejora opcional futura, no como requisito del MVP.
