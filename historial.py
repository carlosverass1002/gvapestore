import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime

def abrir_historial_ventas():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    def cargar_clientes():
        cursor.execute("SELECT nombre FROM clientes")
        return ["Todos"] + [row[0] for row in cursor.fetchall()]

    def buscar():
        cliente = cliente_cb.get()
        desde = desde_entry.get()
        hasta = hasta_entry.get()

        query = """
            SELECT v.id, c.nombre, p.nombre, v.cantidad, v.total, v.fecha
            FROM ventas v
            JOIN clientes c ON v.cliente_id = c.id
            JOIN productos p ON v.producto_id = p.id
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

        tabla.delete(*tabla.get_children())
        cursor.execute(query, params)
        for row in cursor.fetchall():
            tabla.insert('', 'end', values=row)

    # --- Interfaz ---
    ventana = tk.Toplevel()
    ventana.title("Historial de Ventas")
    ventana.geometry("800x500")

    filtros_frame = tk.Frame(ventana)
    filtros_frame.pack(pady=10)

    tk.Label(filtros_frame, text="Cliente:").grid(row=0, column=0)
    cliente_cb = ttk.Combobox(filtros_frame, values=cargar_clientes(), state="readonly")
    cliente_cb.grid(row=0, column=1)
    cliente_cb.set("Todos")

    tk.Label(filtros_frame, text="Desde (AAAA-MM-DD):").grid(row=0, column=2)
    desde_entry = tk.Entry(filtros_frame)
    desde_entry.grid(row=0, column=3)

    tk.Label(filtros_frame, text="Hasta (AAAA-MM-DD):").grid(row=0, column=4)
    hasta_entry = tk.Entry(filtros_frame)
    hasta_entry.grid(row=0, column=5)

    tk.Button(filtros_frame, text="Buscar", command=buscar).grid(row=0, column=6, padx=5)

    tabla = ttk.Treeview(ventana, columns=("ID", "Cliente", "Producto", "Cantidad", "Total", "Fecha"), show="headings")
    for col in ("ID", "Cliente", "Producto", "Cantidad", "Total", "Fecha"):
        tabla.heading(col, text=col)
        tabla.column(col, anchor="center")

    tabla.pack(expand=True, fill="both", padx=10, pady=10)
    buscar()