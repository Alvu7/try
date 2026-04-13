# Laboratorio de Grafos: Rutas Aéreas (`flights_final.csv`)

Proyecto en Python para **Estructura de Datos II** con solución modular, sin librerías de grafos para los algoritmos principales.

## ✅ Qué cumple esta solución

- Grafo **simple, no dirigido y ponderado**.
- Vértice = aeropuerto, arista = ruta aérea.
- Peso de arista con **distancia Haversine**.
- **Deduplicación** de rutas `A-B` y `B-A`.
- Estructura por **lista de adyacencia**.
- Menú por consola.
- Generación de mapas HTML:
  - `map_aeropuertos.html`
  - `map_camino_minimo.html`

## Estructura del proyecto

- `airport.py`: entidad `Airport`.
- `utils.py`: funciones auxiliares (`haversine_km`, normalización de código).
- `graph.py`: implementación del grafo y algoritmos.
- `loader.py`: carga y limpieza del CSV.
- `map_view.py`: visualización en mapa (Folium).
- `main.py`: menú interactivo en consola.

## Algoritmos implementados

1. **Conexidad y componentes**
   - BFS para hallar componentes conexas.
2. **Bipartito**
   - BFS con coloreo binario (0/1), sobre la componente más grande.
3. **Árbol de expansión mínima (MST)**
   - Kruskal por cada componente conexa.
4. **Caminos mínimos**
   - Dijkstra con `heapq`.
5. **Distancias geográficas**
   - Fórmula de Haversine.

## Requisitos

- Python 3.10+
- Dependencia opcional para mapas:

```bash
pip install folium
```

## Cómo correr

```bash
python main.py
```

Luego:
1. Ingresar la ruta al archivo `flights_final.csv`.
2. Usar el menú para ejecutar cada requerimiento.

## Qué mostrar en la sustentación (guion sugerido)

1. **Modelado del grafo**
   - Explicar por qué es no dirigido y cómo se evita duplicidad con `tuple(sorted((A,B)))`.
2. **Complejidad**
   - Componentes/Bipartición: `O(V + E)`.
   - Dijkstra: `O((V + E) log V)`.
   - Kruskal: `O(E log E)`.
3. **Evidencia funcional**
   - Mostrar salida de:
     - conectividad/componentes,
     - bipartición,
     - MST por componente,
     - top 10 caminos mínimos más largos desde un origen,
     - camino mínimo entre dos aeropuertos.
4. **Visualización**
   - Abrir `map_aeropuertos.html` y `map_camino_minimo.html` en navegador.
5. **Decisiones de diseño**
   - Separación por módulos.
   - Reutilización de funciones (`dijkstra`, `print_airport_info`, etc.).
   - Manejo de errores de entrada.

## Notas

- No se usan librerías de grafos para resolver conectividad, MST, bipartición ni caminos mínimos.
- Si no hay camino entre dos aeropuertos de diferentes componentes, se informa explícitamente.
