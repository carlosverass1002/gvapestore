import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime

class HistorialVentas:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.ventana = tk.Toplevel(self.root)
        self.ventana.title("Historial de Ventas")
        self.ventana.geometry("800x500")
        
        self.conn = sqlite3.connect(self.app.db_path)
        self.cursor = self.conn.cursor()

        self.filtros_frame = tk.Frame(self.ventana)
        self.filtros_frame.pack(pady=10)

        tk.Label(self.filtros_frame, text="Cliente:").grid(row=0, column=0)
        self.cliente_cb = ttk.Combobox(self.filtros_frame, values=self.cargar_clientes(), state="readonly")
        self.cliente_cb.grid(row=0, column=1)
        self.cliente_cb.set("Todos")

        tk.Label(self.filtros_frame, text="Desde (AAAA-MM-DD):").grid(row=0, column=2)
        self.desde_entry = tk.Entry(self.filtros_frame)
        self.desde_entry.grid(row=0, column=3)

        tk.Label(self.filtros_frame, text="Hasta (AAAA-MM-DD):").grid(row=0, column=4)
        self.hasta_entry = tk.Entry(self.filtros_frame)
        self.hasta_entry.grid(row=0, column=5)

        tk.Button(self.filtros_frame, text="Buscar", command=self.buscar).grid(row=0, column=6, padx=5)

        self.tabla = ttk.Treeview(self.ventana, columns=("ID", "Cliente", "Producto", "Cantidad", "Total", "Fecha"), show="headings")
        for col in ("ID", "Cliente", "Producto", "Cantidad", "Total", "Fecha"):
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center")

        self.tabla.pack(expand=True, fill="both", padx=10, pady=10)
        tk.Button(self.ventana, text="Cerrar", command=self.cerrar).pack(pady=5)
        self.buscar()

    def cargar_clientes(self):
        print("Cargando clientes")
        try:
            self.cursor.execute("SELECT nombre FROM clientes")
            return ["Todos"] + [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error cargando clientes: {e}")
            return ["Todos"]

    def buscar(self):
        print("Buscando ventas")
        try:
            cliente = self.cliente_cb.get()
            desde = self.desde_entry.get()
            hasta = self.hasta_entry.get()

            query = """
                SELECT v.id, c.nombre, p.nombre, dv.cantidad, dv.total, v.fecha
                FROM ventas v
                LEFT JOIN clientes c ON v.cliente_id = c.id
                JOIN detalles_venta dv ON v.id = dv.venta_id
                JOIN productos p ON dv.producto_id = p.id
                WHERE 1=1
            """
            params = []

            if cliente and cliente != "Todos":
                query += " AND c.nombre = ?"
                params.append(cliente)

            if desde:
                query += " AND v.fecha >= ?"
                params.append(desde + " 00:00:00")
            if hasta:
                query += " AND v.fecha <= ?"
                params.append(hasta + " 23:59:59")

            self.tabla.delete(*self.tabla.get_children())
            self.cursor.execute(query, params)
            for row in self.cursor.fetchall():
                self.tabla.insert('', 'end', values=row)
        except sqlite3.Error as e:
            print(f"Error buscando ventas: {e}")
            tk.messagebox.showerror("Error", f"Error al buscar ventas: {e}")

    def cerrar(self):
        print("Cerrando ventana de historial")
        self.conn.close()
        self.ventana.destroy()