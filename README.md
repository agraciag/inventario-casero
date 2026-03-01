# Inventario Casero

App casera para organizar cajas e items cuando te mudas. Hecha para usarse desde el celular.

## Capturas de pantalla

<!-- TODO: agregar capturas -->

## Que hace

- Creas cajas, les pones numero y etiqueta
- Agregas items con foto, nombre y prioridad
- Cada item se clasifica por prioridad de envio (prioritario, no prioritario, quizas, no vale la pena, tirar/regalar/vender)
- Vista "Organizar" con drag-and-drop para mover items entre cajas rapidamente
- Codigos QR por caja para escanear y ver el contenido
- Reporte resumen con conteos y peso total

## Tech stack

- **Backend**: Python + FastAPI
- **Base de datos**: SQLite (via SQLAlchemy)
- **Frontend**: Jinja2 templates + htmx + Tailwind CSS
- **Fotos**: Pillow para redimensionar, HTML5 camera API para captura
- **Auth**: PIN por usuario con cookies firmadas
- **Drag-and-drop**: SortableJS

## Como correrlo

```bash
pip install -r requirements.txt
python seed.py        # Crea la BD y usuarios iniciales
python run.py         # Servidor en puerto 8070
```

Abrir http://localhost:8070 en el navegador.

## Licencia

MIT
