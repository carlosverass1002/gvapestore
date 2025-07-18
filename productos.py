import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class ProductosScreen:
    def __init__(self, root, app):
        print("Initializing ProductosScreen")
        self.root = root
        self.app = app
        
        # Verificar que el usuario sea Admin
        if self.app.current_role != "Admin":
            messagebox.showerror("Error", "Acceso denegado. Solo los administradores pueden acceder a Productos.")
            self.app.show_main_menu(self.app.current_user, self.app.current_role)
            return
        
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Botones
        tk.Button(self.frame, text="Agregar Producto", command=self.agregar_producto).pack(pady=5)
        tk.Button(self.frame, text="Editar Producto", command=self.editar_producto).pack(pady=5)
        tk.Button(self.frame, text="Eliminar Producto", command=self.eliminar_producto).pack(pady=5)
        tk.Button(self.frame, text="Volver", command=lambda: self.app.show_main_menu(self.app.current_user, self.app.current_role)).pack(pady=5)
        
        # Tabla de productos
        self.tabla = ttk.Treeview(self.frame, columns=("Código", "Nombre", "Precio", "Stock"), show="headings")
        self.tabla.heading("Código", text="Código")
        self.tabla.heading("Nombre", text="Nombre")
        self.tabla.heading("Precio", text="Precio")
        self.tabla.heading("Stock", text="Stock")
        self.tabla.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.cargar_productos()

    def cargar_productos(self):
        print("Loading products")
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        try:
            conn = sqlite3.connect(self.app.db_path)
            c = conn.cursor()
            c.execute("SELECT codigo, nombre, precio, stock FROM productos")
            for row in c.fetchall():
                self.tabla.insert("", "end", values=row)
            conn.close()
        except sqlite3.Error as e:
            print(f"Error loading products: {e}")
            messagebox.showerror("Error", f"Error al cargar productos: {e}")

    def agregar_producto(self):
        print("Opening add product window")
        ventana = tk.Toplevel(self.root)
        ventana.title("Agregar Producto")
        ventana.geometry("300x300")
        ventana.transient(self.root)
        ventana.grab_set()
        
        tk.Label(ventana, text="Código:").pack(pady=5)
        codigo_entry = tk.Entry(ventana)
        codigo_entry.pack(pady=5)
        
        tk.Label(ventana, text="Nombre:").pack(pady=5)
        nombre_entry = tk.Entry(ventana)
        nombre_entry.pack(pady=5)
        
        tk.Label(ventana, text="Precio:").pack(pady=5)
        precio_entry = tk.Entry(ventana)
        precio_entry.pack(pady=5)
        
        tk.Label(ventana, text="Stock (opcional):").pack(pady=5)
        stock_entry = tk.Entry(ventana)
        stock_entry.pack(pady=5)
        
        def guardar():
            codigo = codigo_entry.get().strip()
            nombre = nombre_entry.get().strip()
            precio = precio_entry.get().strip()
            stock = stock_entry.get().strip() or None
            if not codigo or not nombre or not precio:
                messagebox.showerror("Error", "Código, nombre y precio son obligatorios")
                return
            try:
                precio = float(precio)
                if stock:
                    stock = int(stock)
                conn = sqlite3.connect(self.app.db_path)
                c = conn.cursor()
                c.execute("INSERT INTO productos (codigo, nombre, precio, stock) VALUES (?, ?, ?, ?)", (codigo, nombre, precio, stock))
                conn.commit()
                conn.close()
                self.cargar_productos()
                ventana.grab_release()
                ventana.destroy()
                messagebox.showinfo("Éxito", "Producto agregado correctamente")
            except ValueError:
                messagebox.showerror("Error", "Precio y stock deben ser numéricos")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error al agregar producto: {e}")
                print(f"Error adding product: {e}")
        
        tk.Button(ventana, text="Guardar", command=guardar).pack(pady=10)
        tk.Button(ventana, text="Cancelar", command=lambda: [ventana.grab_release(), ventana.destroy()]).pack(pady=5)

    def editar_producto(self):
        print("Opening edit product window")
        selected = self.tabla.selection()
        if not selected:
            messagebox.showerror("Error", "Seleccione un producto")
            return
        codigo = self.tabla.item(selected[0])["values"][0]
        
        ventana = tk.Toplevel(self.root)
        ventana.title("Editar Producto")
        ventana.geometry("300x300")
        ventana.transient(self.root)
        ventana.grab_set()
        
        conn = sqlite3.connect(self.app.db_path)
        c = conn.cursor()
        c.execute("SELECT nombre, precio, stock FROM productos WHERE codigo = ?", (codigo,))
        nombre, precio, stock = c.fetchone()
        conn.close()
        
        tk.Label(ventana, text=f"Código: {codigo}").pack(pady=5)
        tk.Label(ventana, text="Nombre:").pack(pady=5)
        nombre_entry = tk.Entry(ventana)
        nombre_entry.insert(0, nombre)
        nombre_entry.pack(pady=5)
        
        tk.Label(ventana, text="Precio:").pack(pady=5)
        precio_entry = tk.Entry(ventana)
        precio_entry.insert(0, str(precio))
        precio_entry.pack(pady=5)
        
        tk.Label(ventana, text="Stock (opcional):").pack(pady=5)
        stock_entry = tk.Entry(ventana)
        stock_entry.insert(0, str(stock) if stock is not None else "")
        stock_entry.pack(pady=5)
        
        def guardar():
            nombre = nombre_entry.get().strip()
            precio = precio_entry.get().strip()
            stock = stock_entry.get().strip() or None
            if not nombre or not precio:
                messagebox.showerror("Error", "Nombre y precio son obligatorios")
                return
            try:
                precio = float(precio)
                if stock:
                    stock = int(stock)
                conn = sqlite3.connect(self.app.db_path)
                c = conn.cursor()
                c.execute("UPDATE productos SET nombre = ?, precio = ?, stock = ? WHERE codigo = ?", (nombre, precio, stock, codigo))
                conn.commit()
                conn.close()
                self.cargar_productos()
                ventana.grab_release()
                ventana.destroy()
                messagebox.showinfo("Éxito", "Producto actualizado correctamente")
            except ValueError:
                messagebox.showerror("Error", "Precio y stock deben ser numéricos")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error al actualizar producto: {e}")
                print(f"Error updating product: {e}")
        
        tk.Button(ventana, text="Guardar", command=guardar).pack(pady=10)
        tk.Button(ventana, text="Cancelar", command=lambda: [ventana.grab_release(), ventana.destroy()]).pack(pady=5)

    def eliminar_producto(self):
        print("Deleting product")
        selected = self.tabla.selection()
        if not selected:
            messagebox.showerror("Error", "Seleccione un producto")
            return
        codigo = self.tabla.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar producto con código {codigo}?"):
            try:
                conn = sqlite3.connect(self.app.db_path)
                c = conn.cursor()
                c.execute("DELETE FROM productos WHERE codigo = ?", (codigo,))
                conn.commit()
                conn.close()
                self.cargar_productos()
                messagebox.showinfo("Éxito", "Producto eliminado correctamente")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error al eliminar producto: {e}")
                print(f"Error deleting product: {e}")