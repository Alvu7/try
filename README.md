# Laboratorio de Aeropuertos (interfaz gráfica)

Este proyecto permite **cargar un Excel/CSV desde una interfaz gráfica** y ejecutar todo el análisis automáticamente.

## Qué hace

- Importa `.xlsx`, `.xls` o `.csv`.
- Normaliza columnas de origen/destino y valida nulos/coordenadas.
- Construye un grafo no dirigido y ponderado con distancia Haversine.
- Calcula:
  - componentes conectados,
  - bipartición global y de componente mayor,
  - peso del MST por componente,
  - top 10 caminos más largos desde un aeropuerto,
  - camino mínimo entre dos aeropuertos.
- Guarda la salida completa en `resultado_analisis.json`.

## Uso rápido (GUI)

1. Ejecuta:

```bash
python main.py
```

2. Haz clic en **Seleccionar** y elige el Excel/CSV.
3. (Opcional) escribe código de aeropuerto origen/destino.
4. Haz clic en **Procesar archivo**.
5. Revisa el resultado en pantalla y en `resultado_analisis.json`.

## Columnas requeridas

Se aceptan alias en español/inglés, pero el esquema canónico es:

- `origin_code`, `origin_name`, `origin_city`, `origin_country`, `origin_lat`, `origin_lon`
- `destination_code`, `destination_name`, `destination_city`, `destination_country`, `destination_lat`, `destination_lon`

## Estructura

- `src/io/importer.py`: carga/validación.
- `src/graph/airport_graph.py`: grafo y algoritmos.
- `src/services/pipeline.py`: casos de uso de análisis.
- `src/ui/gui_app.py`: interfaz gráfica con Tkinter.
- `main.py`: punto de entrada de la GUI.
- `tests/test_airport_graph.py`: prueba base de algoritmos.
