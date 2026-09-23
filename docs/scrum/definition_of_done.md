# Definition of Done (DoD)

> Ver también: [Product Backlog](product_backlog.md) · [Estimación](estimation.md) · [Arquitectura](../architecture/overview.md)

Una historia de usuario se considera "Done" cuando cumple TODO lo siguiente:

1. Código implementado y fusionado, siguiendo la arquitectura definida en [architecture/overview.md](../architecture/overview.md).
2. Todos los criterios de aceptación de la historia verificados manualmente o con test automatizado.
3. Pruebas unitarias/integración relevantes escritas y en verde, corriendo tanto local (`pytest`) como en Docker (`docker-compose run test`).
4. Si la historia toca el flujo de empaquetado o el .exe final: probado en una máquina/VM sin Docker y sin Python instalado.
5. Si la historia integra la API de Claude: confirmado que la app sigue funcionando sin API key configurada (modo local).
6. Documentación actualizada (README y/o docs/ relevantes) si el cambio afecta cómo se instala, configura o usa la app.
7. Sin secretos (API keys) hardcodeados ni commiteados al repositorio.
