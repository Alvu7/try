from __future__ import annotations

import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from src.io.importer import load_dataset
from src.services.pipeline import analyze_graph


class AirportApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Laboratorio de Aeropuertos")
        self.geometry("980x700")

        self.file_path_var = tk.StringVar()
        self.source_var = tk.StringVar()
        self.target_var = tk.StringVar()

        self._build_ui()

    def _build_ui(self) -> None:
        top = tk.Frame(self)
        top.pack(fill="x", padx=12, pady=12)

        tk.Label(top, text="Archivo Excel/CSV:").grid(row=0, column=0, sticky="w")
        tk.Entry(top, textvariable=self.file_path_var, width=80).grid(row=0, column=1, padx=8)
        tk.Button(top, text="Seleccionar", command=self.select_file).grid(row=0, column=2)

        tk.Label(top, text="Origen (opcional):").grid(row=1, column=0, sticky="w", pady=(10, 0))
        tk.Entry(top, textvariable=self.source_var, width=20).grid(row=1, column=1, sticky="w", padx=8, pady=(10, 0))

        tk.Label(top, text="Destino (opcional):").grid(row=2, column=0, sticky="w", pady=(8, 0))
        tk.Entry(top, textvariable=self.target_var, width=20).grid(row=2, column=1, sticky="w", padx=8, pady=(8, 0))

        tk.Button(top, text="Procesar archivo", command=self.run_pipeline, bg="#1f6feb", fg="white").grid(
            row=3, column=1, sticky="w", pady=(12, 0)
        )

        self.status_label = tk.Label(self, text="Listo para cargar archivo", anchor="w")
        self.status_label.pack(fill="x", padx=12)

        self.output = tk.Text(self, wrap="word", height=35)
        self.output.pack(fill="both", expand=True, padx=12, pady=12)
        self.output.configure(font=("Courier", 10))

    def select_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecciona tu Excel/CSV",
            filetypes=[("Data files", "*.xlsx *.xls *.csv"), ("All files", "*.*")],
        )
        if path:
            self.file_path_var.set(path)

    def run_pipeline(self) -> None:
        file_path = self.file_path_var.get().strip()
        if not file_path:
            messagebox.showwarning("Falta archivo", "Selecciona un archivo primero.")
            return

        source = self.source_var.get().strip().upper() or None
        target = self.target_var.get().strip().upper() or None

        try:
            self.status_label.config(text="Procesando...")
            self.update_idletasks()

            graph, stats = load_dataset(file_path)
            result = analyze_graph(graph, source=source, target=target)

            output_path = Path("resultado_analisis.json")
            output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

            payload = {
                "input_file": file_path,
                "load_stats": stats,
                "analysis": result,
                "output_json": str(output_path.resolve()),
            }

            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, json.dumps(payload, indent=2, ensure_ascii=False))
            self.status_label.config(text=f"Listo. Resultado guardado en {output_path}")
        except Exception as exc:
            self.status_label.config(text="Error durante el procesamiento")
            messagebox.showerror("Error", str(exc))


def launch_gui() -> None:
    app = AirportApp()
    app.mainloop()
