# Arquitectura

## Objetivo
App de escritorio para quitar marcas de agua de imágenes (selección múltiple, procesamiento por lotes), que funcione en cualquier PC sin Docker instalado. Docker/docker-compose se usan solo para el entorno de pruebas.

## Stack
- **UI**: Python + PySide6.
- **Empaquetado**: PyInstaller (con plugins de Qt explícitos) → ejecutable standalone (.exe en Windows).
- **Motor de inpainting local**: IOPaint (modelo LaMa), corre embebido/local en la máquina del usuario. Gratis, offline.
- **Asistencia opcional de IA remota**: API de Claude (Anthropic), usada solo para tareas baratas en tokens:
  - Sugerir el bounding box / máscara de la marca de agua a partir de una miniatura.
  - Control de calidad rápido del resultado (¿quedó rastro visible?).
  - Generación de nombres de archivo / reportes de lote.
  - **Nunca** se le envía la imagen completa en alta resolución para "generar" el resultado final: eso lo hace el modelo local.
- **Pruebas**: pytest, ejecutado tanto localmente como dentro de Docker (docker-compose) para reproducibilidad en CI.

## Flujo (pipeline)
1. Usuario abre la app y selecciona una o varias imágenes (multi-select).
2. Para cada imagen:
   a. (Opcional) Claude Vision analiza una miniatura y devuelve la región probable de la marca de agua.
   b. Usuario confirma/ajusta la máscara manualmente si lo desea.
   c. IOPaint (LaMa) local procesa la imagen completa y reconstruye la región.
   d. (Opcional) Claude hace una verificación rápida de calidad sobre el resultado (miniatura).
3. Se guarda el resultado; progreso y cancelación visibles para lotes grandes.

## Modo sin API key
Si el usuario no configura una clave de Anthropic, la app debe seguir funcionando 100% local: selección manual de máscara + IOPaint. La integración con Claude es un *enhancement*, no una dependencia dura.

## Docker (solo pruebas)
- `docker/Dockerfile.test`: entorno reproducible con Python + dependencias + IOPaint para correr la suite de tests.
- `docker-compose.yml`: levanta el contenedor de test (y opcionalmente un servicio IOPaint de referencia) para integración.
- La imagen final distribuible al usuario es el ejecutable de PyInstaller, **no** una imagen Docker.
