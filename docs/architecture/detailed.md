# Arquitectura técnica detallada

> Ver también: [Arquitectura (visión general)](overview.md) · [Product Backlog](../scrum/product_backlog.md)

Complementa [overview.md](overview.md) con el diseño de módulos, interfaces y flujos, sin entrar todavía en código (fase de planeación).

## 1. Layout de carpetas planeado

```
src/watermark_remover/
├── main.py                     # entry point: crea QApplication y MainWindow
├── ui/
│   ├── main_window.py          # MainWindow: layout general, toolbar, menú
│   ├── image_list_widget.py    # lista/galería con multi-select y drag&drop
│   ├── preview_canvas.py       # vista previa + overlay de máscara
│   ├── mask_editor.py          # lógica de dibujo/ajuste de rectángulo o máscara libre
│   ├── progress_dialog.py      # progreso de lote + cancelar
│   └── settings_dialog.py      # configurar host de Ollama, carpeta de salida
├── core/
│   ├── image_item.py           # dataclass: ruta, miniatura, máscara, estado, resultado
│   ├── batch_processor.py      # orquesta la cola de ImageItem por el pipeline (QThread)
│   ├── inpainting_engine.py    # interfaz InpaintingEngine + implementación IOPaintEngine
│   ├── watermark_detector.py   # interfaz WatermarkDetector + OllamaWatermarkDetector + NullDetector
│   └── quality_checker.py      # interfaz QualityChecker + OllamaQualityChecker + NullQualityChecker
├── services/
│   ├── ollama_client.py        # wrapper del cliente Python de Ollama; reduce imagen antes de enviar
│   └── config.py               # carga/guarda config (host de Ollama, carpeta salida)
└── utils/
    ├── image_utils.py          # miniaturas, downscaling, conversión de formato
    └── file_utils.py           # nombres de salida seguros, evita sobrescritura
```

## 2. Principio de diseño clave: Strategy + Null Object

`InpaintingEngine`, `WatermarkDetector` y `QualityChecker` son **interfaces (Strategy)**. Esto permite:
- Que el motor de inpainting sea intercambiable (hoy IOPaint/LaMa local; mañana otro sin tocar el resto de la app).
- Que las funciones de Ollama sean **opcionales**: si Ollama no responde (no está corriendo o no está configurado), `NullDetector`/`NullQualityChecker` se usan automáticamente (Null Object pattern) y la UI oculta esas opciones — nunca hay error por no tenerlo disponible.
- Que en tests (HU-10) se puedan mockear `InpaintingEngine`/`WatermarkDetector` sin depender de IOPaint real ni de red.

```mermaid
classDiagram
    class InpaintingEngine {
        <<interface>>
        +process(image, mask) Image
    }
    class IOPaintEngine {
        +process(image, mask) Image
    }
    class WatermarkDetector {
        <<interface>>
        +detect(thumbnail) BoundingBox
    }
    class OllamaWatermarkDetector {
        +detect(thumbnail) BoundingBox
    }
    class NullDetector {
        +detect(thumbnail) None
    }
    class QualityChecker {
        <<interface>>
        +check(before, after) QCResult
    }
    class OllamaQualityChecker
    class NullQualityChecker

    InpaintingEngine <|.. IOPaintEngine
    WatermarkDetector <|.. OllamaWatermarkDetector
    WatermarkDetector <|.. NullDetector
    QualityChecker <|.. OllamaQualityChecker
    QualityChecker <|.. NullQualityChecker
```

## 3. Componentes y responsabilidades

```mermaid
flowchart TB
    subgraph UI["UI (PySide6)"]
        MW[MainWindow]
        ILW[ImageListWidget]
        PC[PreviewCanvas]
        ME[MaskEditor]
        PD[ProgressDialog]
        SD[SettingsDialog]
    end

    subgraph CORE["core/"]
        BP[BatchProcessor - QThread]
        IE[InpaintingEngine]
        WD[WatermarkDetector]
        QC[QualityChecker]
    end

    subgraph SVC["services/"]
        CC[OllamaClient]
        CFG[Config / keyring]
    end

    MW --> ILW
    MW --> PC
    PC --> ME
    MW --> SD
    SD --> CFG
    MW --> BP
    BP --> PD
    BP --> IE
    BP --> WD
    BP --> QC
    WD --> CC
    QC --> CC
    CC --> CFG
```

## 4. Flujo — imagen individual (con asistencia opcional de Ollama)

```mermaid
sequenceDiagram
    actor U as Usuario
    participant PC as PreviewCanvas
    participant WD as WatermarkDetector
    participant ME as MaskEditor
    participant IE as InpaintingEngine (IOPaint local)
    participant QC as QualityChecker

    U->>PC: selecciona imagen de la lista
    opt Ollama disponible
        U->>WD: click "Detectar automáticamente"
        WD->>WD: genera miniatura (baja resolución)
        WD-->>ME: bounding box sugerido
    end
    U->>ME: ajusta/dibuja máscara manualmente
    U->>IE: click "Procesar"
    IE-->>IE: inpainting local (sin red, sin Docker)
    IE-->>PC: imagen resultado
    opt Ollama disponible
        IE->>QC: miniatura antes/después
        QC-->>U: alerta si detecta rastro visible
    end
    U->>PC: confirma y guarda resultado
```

## 5. Flujo — procesamiento por lotes

```mermaid
sequenceDiagram
    actor U as Usuario
    participant MW as MainWindow
    participant BP as BatchProcessor (QThread)
    participant IE as InpaintingEngine
    participant PD as ProgressDialog

    U->>MW: click "Procesar todas" (N imágenes)
    MW->>BP: start(cola de ImageItem)
    BP->>PD: abre diálogo de progreso
    loop por cada imagen (hasta cancelar)
        BP->>IE: process(imagen, máscara)
        IE-->>BP: resultado u error
        BP->>PD: actualiza progreso (X/N)
        alt error en esta imagen
            BP->>BP: registra error, continúa con la siguiente
        end
        alt usuario cancela
            BP->>BP: detiene el bucle, no corrompe ya guardadas
        end
    end
    BP-->>MW: resumen final (éxitos/errores)
```

## 6. Manejo de configuración

- No hay secretos que proteger para Ollama (es local, sin API key). Lo único configurable es el **host** (`OLLAMA_HOST`, por defecto `http://localhost:11434`), para poder apuntar a otra máquina de la red que corra el modelo.
- `services/config.py` persiste ese host (y el modelo a usar) en config local, no versionada.
- `SettingsDialog` permite editarlo en tiempo de ejecución, y probar la conexión ("Verificar Ollama").
- Si Ollama no responde en ese host → `OllamaWatermarkDetector`/`OllamaQualityChecker` no se instancian; se usan `NullDetector`/`NullQualityChecker` y la UI oculta los botones correspondientes.

## 7. Puntos de prueba (testability) pensados para HU-10

- `InpaintingEngine` y `WatermarkDetector` son interfaces → en tests se inyectan fakes/mocks, sin necesitar IOPaint real ni red.
- `BatchProcessor` se prueba con una cola de `ImageItem` falsos y un engine mock que simula éxito/error, verificando que el lote continúa tras un fallo individual (AC de HU-8).
- `OllamaClient` se prueba con el cliente Python de Ollama mockeado (sin llamadas reales) para validar que reduce la imagen antes de "enviarla" y que maneja la ausencia de Ollama (host no responde) sin lanzar excepción.
