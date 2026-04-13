# Laboratorio de Aeropuertos (carga en 1 paso)

Este proyecto ahora permite **cargar un Excel/CSV y ejecutar todo el pipeline automáticamente**.

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

## Uso rápido (solo meter Excel y listo)

1. Ejecuta:

```bash
python main.py
```

2. Selecciona el archivo en el diálogo (o pega la ruta si no hay GUI).
3. (Opcional) ingresa código origen/destino para consultas.

## Columnas requeridas

Se aceptan alias en español/inglés, pero el esquema canónico es:

- `origin_code`, `origin_name`, `origin_city`, `origin_country`, `origin_lat`, `origin_lon`
- `destination_code`, `destination_name`, `destination_city`, `destination_country`, `destination_lat`, `destination_lon`

## Estructura

- `src/io/importer.py`: carga/validación.
- `src/graph/airport_graph.py`: grafo y algoritmos.
- `src/services/pipeline.py`: casos de uso de análisis.
- `main.py`: punto de entrada único.
- `tests/test_airport_graph.py`: prueba base de algoritmos.
