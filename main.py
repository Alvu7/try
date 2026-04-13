from __future__ import annotations

import json
from pathlib import Path

from src.io.importer import load_dataset
from src.services.pipeline import analyze_graph


def pick_file() -> str:
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Selecciona tu Excel/CSV",
            filetypes=[("Data files", "*.xlsx *.xls *.csv"), ("All files", "*.*")],
        )
        root.destroy()
        if file_path:
            return file_path
    except Exception:
        pass

    return input("Ruta del archivo Excel/CSV: ").strip()


def main() -> None:
    print("=== Laboratorio de Aeropuertos ===")
    file_path = pick_file()
    if not file_path:
        print("No seleccionaste archivo.")
        return

    graph, stats = load_dataset(file_path)
    print("\nCarga completada:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    source = input("\nCódigo aeropuerto origen para análisis (Enter = automático): ").strip().upper() or None
    target = input("Código aeropuerto destino para camino mínimo (opcional): ").strip().upper() or None

    result = analyze_graph(graph, source=source, target=target)

    output_path = Path("resultado_analisis.json")
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\nResumen:")
    print(f"- Componentes conectados: {result['num_components']}")
    print(f"- Tamaños componentes: {result['component_sizes'][:10]}")
    print(f"- Bipartito (global): {result['is_bipartite_global']}")
    print(f"- Bipartito (componente mayor): {result['is_bipartite_largest_component']}")
    print(f"- Peso MST por componente (km): {result['mst_weight_by_component_km'][:10]}")
    if result["source"]:
        print(f"- Top 10 caminos más largos desde {result['source']}: {result['top_10_longest_shortest_paths']}")
    if result["shortest_path_query"]:
        print(f"- Camino mínimo: {result['shortest_path_query']}")

    print(f"\nResultado completo guardado en: {output_path}")


if __name__ == "__main__":
    main()
