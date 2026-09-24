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
pip install pyinstaller
pyinstaller --name QuitarMarcaDeAgua --windowed --paths src src/watermark_remover/main.py --noconfirm
```
El resultado queda en `dist/QuitarMarcaDeAgua/` (~110MB). Los plugins de Qt (`qwindows`, etc.) se incluyen automáticamente gracias al hook `pyi_rth_pyside6.py` que trae PyInstaller — no requiere configuración manual adicional.

**Importante — requisito de IOPaint:** el `.exe` empaqueta toda la UI y la lógica de la app (funciona standalone, verificado arrancando con un `PATH` mínimo simulando una máquina limpia). Sin embargo, **no empaqueta IOPaint** (el motor de inpainting): nuestro código lo invoca como proceso externo (`iopaint run ...`), no como librería Python importada, así que PyInstaller no lo detecta ni lo incluye. Si IOPaint no está instalado en la máquina destino, la app arranca y funciona normalmente (cargar imágenes, marcar máscara, etc.) pero el botón "Procesar" falla con un mensaje de error claro (no crashea) pidiendo instalar IOPaint.

Antes de distribuir el `.exe` a un usuario final, instala IOPaint en esa máquina una sola vez:
```
pip install iopaint
```
(Esto sí requiere Python en la máquina destino, solo para este paso — es una limitación conocida, documentada como pendiente en el roadmap: empaquetar IOPaint completo junto al `.exe` requeriría bundlear PyTorch, lo cual es significativamente más complejo y pesado, y quedó fuera del alcance de este sprint.)

**Troubleshooting:**
- Si el `.exe` no arranca y no muestra ningún error visible, ejecútalo desde una consola (`QuitarMarcaDeAgua.exe` en vez de doble-clic) para ver el traceback.
- Si ves errores de plugin de Qt (`could not find or load the Qt platform plugin`), verifica que la carpeta `_internal/PySide6/plugins/platforms/` exista junto al `.exe` — no muevas el `.exe` fuera de su carpeta `_internal`.
