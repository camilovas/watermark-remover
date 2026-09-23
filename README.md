# Quitar Marca de Agua

App de escritorio para eliminar marcas de agua de imágenes (selección múltiple / por lotes), con IA local (IOPaint/LaMa) complementada opcionalmente por la API de Claude para tareas baratas (detección de región). Funciona en cualquier PC **sin Docker**; Docker/docker-compose se usan solo para pruebas.

## Documentación
- [Investigación y mejores prácticas](docs/research/best_practices.md)
- [Arquitectura](docs/architecture/overview.md) · [Arquitectura detallada (módulos, diagramas)](docs/architecture/detailed.md)
- [Product Backlog (Scrum)](docs/scrum/product_backlog.md)
- [Estimación general del backlog](docs/scrum/estimation.md)
- [DoD base del proyecto](docs/scrum/dod_base.md)
- [Sprint 0](docs/scrum/sprints/sprint-0/plan.md) (con su propia [estimación](docs/scrum/sprints/sprint-0/estimation.md) y [DoD](docs/scrum/sprints/sprint-0/definition_of_done.md))

## Desarrollo local (sin Docker)
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

## Pruebas con Docker
```
docker-compose up --build test
```

## Configurar Claude API (opcional)
La app funciona 100% local sin esto. Para habilitar la sugerencia automática de región de marca de agua:
```
set ANTHROPIC_API_KEY=tu_api_key
```

## Empaquetado como ejecutable (sin Docker, sin Python en la máquina destino)
```
pyinstaller --name QuitarMarcaDeAgua --windowed src/watermark_remover/main.py
```
