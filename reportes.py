import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime
import pandas as pd
import os

class ReportesScreen:
    def __init__(self, root, app, mode):
        print(f"Inicializando ReportesScreen en modo: {mode}")
        self.root = root
        self.app = app
        self.mode = mode
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        if self.mode == "historial":
            self.mostrar_historial_ventas()
        elif self.mode == "reportes":
            self.mostrar_reportes()

    def mostrar_historial_ventas(self):
        print("Mostrando historial de ventas")
        try:
            tk.Label(self.frame, text="Historial de Ventas", font=("Arial", 16)).grid(row=0, column=0, columnspan=3, pady=10)
            
            # Tabla de ventas
            self.tree = ttk.Treeview(self.frame, columns=("ID", "Fecha", "Cliente", "Usuario", "Total", "Método"), show="headings")
            self.tree.heading("ID", text="ID")
            self.tree.heading("Fecha", text="Fecha")
            self.tree.heading("Cliente", text="Cliente")
            self.tree.heading("Usuario", text="Usuario")
            self.tree.heading("Total", text="Total (RD$)")
            self.tree.heading("Método", text="Método de Pago")
            self.tree.column("ID", width=50)
            self.tree.column("Fecha", width=150)
            self.tree.column("Cliente", width=150)
            self.tree.column("Usuario", width=100)
            self.tree.column("Total", width=100)
            self.tree.column("Método", width=100)
            self.tree.grid(row=1, column=0, columnspan=3, pady=10)
            
            # Botón para ver detalles
            tk.Button(self.frame, text="Ver Detalles", command=self.ver_detalles_venta).grid(row=2, column=0, columnspan=3, pady=5)
            tk.Button(self.frame, text="Volver", command=lambda: self.app.show_main_menu(self.app.current_user, self.app.current_role)).grid(row=3, column=0, columnspan=3, pady=5)
            
            self.actualizar_historial()
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar historial: {e}")
            print(f"Error mostrando historial: {e}")

    def actualizar_historial(self):
        print("Actualizando historial de ventas")
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            conn = sqlite3.connect(self.app.db_path)
            c = conn.cursor()
            c.execute("""
                SELECT v.id, v.fecha, c.nombre, u.usuario, v.total, v.metodo_pago
                FROM ventas v
                LEFT JOIN clientes c ON v.cliente_id = c.id
                LEFT JOIN usuarios u ON v.usuario_id = u.id
            """)
            for row in c.fetchall():
                cliente = row[2] if row[2] else "Sin Cliente"
                self.tree.insert("", "end", values=(row[0], row[1], cliente, row[3], f"RD${row[4]:.2f}", row[5]))
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al actualizar historial: {e}")
            print(f"Error actualizando historial: {e}")

    def ver_detalles_venta(self):
        print("Abriendo detalles de venta")
        try:
            selected_item = self.tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "Seleccione una venta para ver detalles")
                return
            
            venta_id = self.tree.item(selected_item)["values"][0]
            ventana = tk.Toplevel(self.root)
            ventana.title(f"Detalles de Venta ID {venta_id}")
            ventana.geometry("500x400")
            
            tree = ttk.Treeview(ventana, columns=("Producto", "Cantidad", "Precio", "Total"), show="headings")
            tree.heading("Producto", text="Producto")
            tree.heading("Cantidad", text="Cantidad")
            tree.heading("Precio", text="Precio Unitario (RD$)")
            tree.heading("Total", text="Total (RD$)")
            tree.column("Producto", width=200)
            tree.column("Cantidad", width=80)
            tree.column("Precio", width=100)
            tree.column("Total", width=100)
            tree.pack(pady=10, padx=10, fill="both", expand=True)
            
            conn = sqlite3.connect(self.app.db_path)
            c = conn.cursor()
            c.execute("""
                SELECT p.nombre, dv.cantidad, dv.precio_unitario, dv.total
                FROM detalles_venta dv
                JOIN productos p ON dv.producto_id = p.id
                WHERE dv.venta_id = ?
            """, (venta_id,))
            for row in c.fetchall():
                tree.insert("", "end", values=(row[0], row[1], f"RD${row[2]:.2f}", f"RD${row[3]:.2f}"))
            conn.close()
            
            tk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(pady=5)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al mostrar detalles: {e}")
            print(f"Error mostrando detalles: {e}")

    def mostrar_reportes(self):
        print("Mostrando panel de reportes")
        try:
            tk.Label(self.frame, text="Reportes de Ventas", font=("Arial", 16)).grid(row=0, column=0, columnspan=4, pady=10)
            
            # Filtros de fecha
            tk.Label(self.frame, text="Fecha Inicio").grid(row=1, column=0, sticky="w")
            self.fecha_inicio = DateEntry(self.frame, date_pattern="yyyy-mm-dd")
            self.fecha_inicio.grid(row=1, column=1, sticky="w")
            
            tk.Label(self.frame, text="Fecha Fin").grid(row=1, column=2, sticky="w")
            self.fecha_fin = DateEntry(self.frame, date_pattern="yyyy-mm-dd")
            self.fecha_fin.grid(row=1, column=3, sticky="w")
            
            tk.Button(self.frame, text="Generar Reporte", command=self.generar_reporte).grid(row=2, column=0, columnspan=4, pady=5)
            
            # Área de resultados
            self.resultados_texto = tk.Text(self.frame, height=10, width=60)
            self.resultados_texto.grid(row=3, column=0, columnspan=4, pady=10)
            
            tk.Button(self.frame, text="Exportar a Excel", command=self.exportar_excel).grid(row=4, column=0, columnspan=4, pady=5)
            tk.Button(self.frame, text="Volver", command=lambda: self.app.show_main_menu(self.app.current_user, self.app.current_role)).grid(row=5, column=0, columnspan=4, pady=5)
            
            # Generar reporte inicial (todos los datos)
            self.generar_reporte()
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar reportes: {e}")
            print(f"Error mostrando reportes: {e}")

    def generar_reporte(self):
        print("Generando reporte")
        try:
            self.resultados_texto.delete(1.0, tk.END)
            conn = sqlite3.connect(self.app.db_path)
            c = conn.cursor()
            
            fecha_inicio = self.fecha_inicio.get_date().strftime("%Y-%m-%d")
            fecha_fin = self.fecha_fin.get_date().strftime("%Y-%m-%d")
            
            # Total de ventas
            c.execute("""
                SELECT SUM(total)
                FROM ventas
                WHERE fecha BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin + " 23:59:59"))
            total_ventas = c.fetchone()[0] or 0
            self.resultados_texto.insert(tk.END, f"Total de Ventas: RD${total_ventas:.2f}\n\n")
            
            # Producto más vendido
            c.execute("""
                SELECT p.nombre, SUM(dv.cantidad) as total_vendido
                FROM detalles_venta dv
                JOIN productos p ON dv.producto_id = p.id
                JOIN ventas v ON dv.venta_id = v.id
                WHERE v.fecha BETWEEN ? AND ?
                GROUP BY p.id
                ORDER BY total_vendido DESC
                LIMIT 1
            """, (fecha_inicio, fecha_fin + " 23:59:59"))
            producto_mas_vendido = c.fetchone()
            if producto_mas_vendido:
                self.resultados_texto.insert(tk.END, f"Producto Más Vendido: {producto_mas_vendido[0]} ({producto_mas_vendido[1]} unidades)\n\n")
            else:
                self.resultados_texto.insert(tk.END, "Producto Más Vendido: No hay datos\n\n")
            
            # Método de pago más usado
            c.execute("""
                SELECT metodo_pago, COUNT(*) as conteo
                FROM ventas
                WHERE fecha BETWEEN ? AND ?
                GROUP BY metodo_pago
                ORDER BY conteo DESC
                LIMIT 1
            """, (fecha_inicio, fecha_fin + " 23:59:59"))
            metodo_pago = c.fetchone()
            if metodo_pago:
                self.resultados_texto.insert(tk.END, f"Método de Pago Más Usado: {metodo_pago[0]} ({metodo_pago[1]} veces)\n")
            else:
                self.resultados_texto.insert(tk.END, "Método de Pago Más Usado: No hay datos\n")
            
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al generar reporte: {e}")
            print(f"Error generando reporte: {e}")

    def exportar_excel(self):
        print("Exportando reporte a Excel")
        try:
            fecha_inicio = self.fecha_inicio.get_date().strftime("%Y-%m-%d")
            fecha_fin = self.fecha_fin.get_date().strftime("%Y-%m-%d")
            conn = sqlite3.connect(self.app.db_path)
            
            # Datos para exportar
            df_ventas = pd.read_sql_query("""
                SELECT v.id, v.fecha, c.nombre as cliente, u.usuario, v.total, v.metodo_pago
                FROM ventas v
                LEFT JOIN clientes c ON v.cliente_id = c.id
                LEFT JOIN usuarios u ON v.usuario_id = u.id
                WHERE v.fecha BETWEEN ? AND ?
            """, conn, params=(fecha_inicio, fecha_fin + " 23:59:59"))
            
            df_detalles = pd.read_sql_query("""
                SELECT v.id, p.nombre as producto, dv.cantidad, dv.precio_unitario, dv.total
                FROM detalles_venta dv
                JOIN productos p ON dv.producto_id = p.id
                JOIN ventas v ON dv.venta_id = v.id
                WHERE v.fecha BETWEEN ? AND ?
            """, conn, params=(fecha_inicio, fecha_fin + " 23:59:59"))
            
            os.makedirs("exportaciones/reportes", exist_ok=True)
            fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = f"exportaciones/reportes/reporte_{fecha_actual}.xlsx"
            
            with pd.ExcelWriter(archivo, engine="openpyxl") as writer:
                df_ventas.to_excel(writer, sheet_name="Ventas", index=False)
                df_detalles.to_excel(writer, sheet_name="Detalles_Venta", index=False)
            
            conn.close()
            messagebox.showinfo("Éxito", f"Reporte exportado a {archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar reporte: {e}")
            print(f"Error exportando reporte: {e}")