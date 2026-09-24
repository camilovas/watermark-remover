# Product Backlog

Metodología: Scrum. Ver [DoD base](dod_base.md), [Estimación general](estimation.md), [Roles y ceremonias](roles_ceremonies.md) y el [Roadmap de sprints](roadmap.md) (cada sprint con su propia estimación, DoD y tareas desglosadas).
Los criterios de aceptación se basan en la [investigación de mejores prácticas](../research/best_practices.md).

## Épica 1 — Base del proyecto (Sprint 0)
### HU-1: Entorno de desarrollo y pruebas reproducible
Como desarrollador quiero un entorno Docker de pruebas para poder correr la suite de tests de forma reproducible sin ensuciar mi máquina.
- **AC1**: `docker-compose up test` ejecuta la suite pytest dentro de un contenedor y reporta resultados.
- **AC2**: El contenedor de test NO es requisito para ejecutar la app final (solo para pruebas/CI).
- **AC3**: README documenta cómo correr tests con y sin Docker.

### HU-2: Spike — validar motor de inpainting local (IOPaint/LaMa)
Como equipo quiero validar que IOPaint corre localmente sin internet para confirmar la viabilidad del motor elegido.
- **AC1**: Se procesa una imagen de prueba con marca de agua y se obtiene un resultado sin conexión a internet (tras la descarga inicial del modelo).
- **AC2**: Se documenta el tiempo de procesamiento y requisitos (RAM/CPU/GPU opcional).

### HU-3: Spike — integración con Ollama local
Como equipo quiero probar el envío de una miniatura a Ollama (modelo de visión local) para sugerencia de bounding box, midiendo tiempo de respuesta y calidad del resultado.
- **AC1**: Se documenta el tiempo de respuesta aproximado de una llamada de detección y la precisión observada.
- **AC2**: Se confirma que la app puede operar sin Ollama disponible (modo 100% local/manual).

## Épica 2 — App de escritorio: selección y carga de imágenes
### HU-4: Selección múltiple de imágenes
Como usuario quiero seleccionar varias imágenes a la vez para procesarlas en lote.
- **AC1**: El diálogo de selección permite multi-select (Ctrl/Shift+click) y arrastrar y soltar (drag & drop).
- **AC2**: Se muestra una miniatura y nombre de cada imagen cargada en una lista/galería.
- **AC3**: Formatos soportados mínimos: PNG, JPG/JPEG, WEBP.

## Épica 3 — Remoción de marca de agua
### HU-5: Marcado manual de la región de marca de agua
Como usuario quiero dibujar/ajustar un rectángulo o máscara sobre la imagen para indicar dónde está la marca de agua.
- **AC1**: El usuario puede dibujar, mover y redimensionar el rectángulo/máscara sobre la vista previa.
- **AC2**: Funciona sin necesidad de tener Ollama disponible (modo 100% local).

### HU-6: Sugerencia automática de región vía Ollama (opcional)
Como usuario quiero que la app sugiera automáticamente la región de la marca de agua para ahorrar tiempo.
- **AC1**: Si Ollama está disponible (host configurado y respondiendo), se envía solo una miniatura (baja resolución, ~512px) al modelo de visión local (`moondream` por defecto), no la imagen completa ni un modelo más pesado.
- **AC2**: El usuario puede aceptar, ajustar o rechazar la sugerencia antes de procesar.
- **AC3**: Si Ollama no está disponible, la opción se oculta/deshabilita sin generar errores.

### HU-7: Procesamiento de imagen (inpainting local)
Como usuario quiero que la app elimine la marca de agua de la imagen seleccionada usando el modelo local.
- **AC1**: El procesamiento corre 100% local (IOPaint/LaMa), sin requerir Docker ni internet.
- **AC2**: Se muestra una barra de progreso durante el procesamiento.
- **AC3**: El resultado se puede comparar (antes/después) antes de guardar.

### HU-8: Procesamiento por lotes con progreso y cancelación
Como usuario quiero procesar muchas imágenes de una vez y poder cancelar si es necesario.
- **AC1**: Barra de progreso global (X de N imágenes) y por imagen.
- **AC2**: Botón de cancelar detiene el lote sin corromper archivos ya procesados.
- **AC3**: Errores en una imagen individual no detienen el resto del lote (se reporta al final).

### HU-11 (backlog futuro, fuera de MVP): Motor alternativo de alta calidad (Stable Diffusion)
Como usuario con GPU quiero un "modo alta calidad" opcional para fondos complejos donde LaMa no sea suficiente.
- **AC1**: Disponible solo si se detecta GPU compatible; en su ausencia, la opción se oculta.
- **AC2**: No reemplaza el motor por defecto (LaMa); es una alternativa seleccionable, priorizada solo después del MVP.

## Épica 4 — Distribución
### HU-9: Empaquetado como ejecutable standalone
Como usuario final quiero instalar/ejecutar la app sin instalar Python, Docker ni dependencias manuales.
- **AC1**: `pyinstaller` genera un .exe funcional en una máquina Windows limpia (sin Python instalado).
- **AC2**: Los plugins de plataforma de Qt (qwindows) están incluidos y la app arranca sin errores de plugin.
- **AC3**: Se prueba el .exe en una VM/máquina sin Docker y sin Python, confirmando funcionamiento completo del flujo local.

## Épica 5 — Calidad
### HU-10: Suite de pruebas automatizadas
Como equipo quiero pruebas automatizadas del pipeline de procesamiento para evitar regresiones.
- **AC1**: Cobertura de tests unitarios sobre la lógica de selección/máscara y el wrapper del motor de inpainting (mockeable).
- **AC2**: Tests corren tanto localmente (`pytest`) como en Docker (`docker-compose run test`).
