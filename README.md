# Quitar Marca de Agua

App de escritorio para eliminar marcas de agua de imágenes (selección múltiple / por lotes), con IA local (IOPaint/LaMa) complementada opcionalmente por Ollama (modelo de visión local, ej. `moondream`) para detección de región. Funciona en cualquier PC **sin Docker**; Docker/docker-compose se usan solo para pruebas.

## Documentación
- [Investigación y mejores prácticas](docs/research/best_practices.md)
- [Arquitectura](docs/architecture/overview.md) · [Arquitectura detallada (módulos, diagramas)](docs/architecture/detailed.md)
- [Product Backlog (Scrum)](docs/scrum/product_backlog.md)
- [Estimación general del backlog](docs/scrum/estimation.md)
- [DoD base del proyecto](docs/scrum/dod_base.md)
- [Roles y ceremonias Scrum](docs/scrum/roles_ceremonies.md)
- [Roadmap de sprints](docs/scrum/roadmap.md) — [Sprint 0](docs/scrum/sprints/sprint-0/plan.md) · [Sprint 1](docs/scrum/sprints/sprint-1/plan.md) · [Sprint 2](docs/scrum/sprints/sprint-2/plan.md) · [Sprint 3](docs/scrum/sprints/sprint-3/plan.md)

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

## Configurar Ollama (opcional)
La app funciona 100% local/manual sin esto. Para habilitar la sugerencia automática de región de marca de agua, instala [Ollama](https://ollama.com), descarga un modelo de visión (`ollama pull moondream`) y, si corre en otra máquina de la red en vez de en esta, apunta la app a ese host:
```
set OLLAMA_HOST=http://IP-DE-LA-OTRA-MAQUINA:11434
```

## Empaquetado como ejecutable (sin Docker, sin Python en la máquina destino)
```
pyinstaller --name QuitarMarcaDeAgua --windowed src/watermark_remover/main.py
```
