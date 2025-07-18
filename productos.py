import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
import sqlite3

class ProductosScreen:
    def __init__(self, root, app):
        print("Inicializando ProductosScreen")
        self.root = root
        self.app = app
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Tabla de productos
        self.tree = ttk.Treeview(self.frame, columns=("ID", "Código", "Nombre", "Precio", "Stock"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Código", text="Código")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Precio", text="Precio (RD$)")
        self.tree.heading("Stock", text="Stock")
        self.tree.column("ID", width=50)
        self.tree.column("Código", width=100)
        self.tree.column("Nombre", width=200)
        self.tree.column("Precio", width=100)
        self.tree.column("Stock", width=80)
        self.tree.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Botones de acción
        tk.Button(self.frame, text="Agregar Producto", command=self.abrir_ventana_agregar).grid(row=1, column=0, columnspan=2, pady=5)
        tk.Button(self.frame, text="Editar Producto", command=self.abrir_ventana_editar).grid(row=2, column=0, columnspan=2, pady=5)
        tk.Button(self.frame, text="Eliminar Producto", command=self.eliminar_producto).grid(row=3, column=0, columnspan=2, pady=5)
        tk.Button(self.frame, text="Volver", command=lambda: self.app.show_main_menu(self.app.current_user, self.app.current_role)).grid(row=4, column=0, columnspan=2, pady=5)
        
        self.actualizar_tabla()

    def actualizar_tabla(self):
        print("Actualizando tabla de productos")
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            conn = sqlite3.connect(self.app.db_path)
            c = conn.cursor()
            c.execute("SELECT id, codigo, nombre, precio, stock FROM productos")
            for row in c.fetchall():
                stock_display = str(row[4]) if row[4] is not None else "N/A"
                self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], stock_display))
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al actualizar tabla: {e}")
            print(f"Error actualizando tabla: {e}")

    def abrir_ventana_agregar(self):
        print("Abriendo ventana para agregar producto")
        try:
            ventana = Toplevel(self.root)
            ventana.title("Agregar Producto")
            ventana.geometry("400x300")
            
            tk.Label(ventana, text="Código").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            codigo_entry = tk.Entry(ventana)
            codigo_entry.grid(row=0, column=1, sticky="w")
            
            tk.Label(ventana, text="Nombre").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            nombre_entry = tk.Entry(ventana)
            nombre_entry.grid(row=1, column=1, sticky="w")
            
            tk.Label(ventana, text="Precio (RD$)").grid(row=2, column=0, sticky="w", padx=5, pady=5)
            precio_entry = tk.Entry(ventana)
            precio_entry.grid(row=2, column=1, sticky="w")
            precio_var = tk.DoubleVar()
            precio_slider = tk.Scale(ventana, from_=0, to=1000, resolution=0.01, orient="horizontal", variable=precio_var, length=200)
            precio_slider.grid(row=3, column=0, columnspan=2, pady=5)
            
            # Sincronizar Entry y Slider para Precio
            def update_precio_entry(*args):
                precio_entry.delete(0, tk.END)
                precio_entry.insert(0, f"{precio_var.get():.2f}")
            def update_precio_slider(event):
                try:
                    precio = float(precio_entry.get())
                    if 0 <= precio <= 1000:
                        precio_var.set(precio)
                    else:
                        messagebox.showerror("Error", "Precio debe estar entre 0 y 1000")
                        precio_entry.delete(0, tk.END)
                        precio_entry.insert(0, f"{precio_var.get():.2f}")
                except ValueError:
                    precio_entry.delete(0, tk.END)
                    precio_entry.insert(0, f"{precio_var.get():.2f}")
            precio_var.trace("w", update_precio_entry)
            precio_entry.bind("<KeyRelease>", update_precio_slider)
            
            tk.Label(ventana, text="Stock (opcional)").grid(row=4, column=0, sticky="w", padx=5, pady=5)
            stock_entry = tk.Entry(ventana)
            stock_entry.grid(row=4, column=1, sticky="w")
            stock_var = tk.IntVar()
            stock_slider = tk.Scale(ventana, from_=0, to=100, orient="horizontal", variable=stock_var, length=200)
            stock_slider.grid(row=5, column=0, columnspan=2, pady=5)
            
            # Sincronizar Entry y Slider para Stock
            def update_stock_entry(*args):
                stock_entry.delete(0, tk.END)
                stock_entry.insert(0, str(stock_var.get()))
            def update_stock_slider(event):
                stock = stock_entry.get().strip()
                if stock:
                    try:
                        stock_value = int(stock)
                        if 0 <= stock_value <= 100:
                            stock_var.set(stock_value)
                        else:
                            messagebox.showerror("Error", "Stock debe estar entre 0 y 100")
                            stock_entry.delete(0, tk.END)
                            stock_entry.insert(0, str(stock_var.get()))
                    except ValueError:
                        stock_entry.delete(0, tk.END)
                        stock_entry.insert(0, str(stock_var.get()))
            stock_var.trace("w", update_stock_entry)
            stock_entry.bind("<KeyRelease>", update_stock_slider)
            
            def guardar():
                print("Guardando nuevo producto")
                try:
                    codigo = codigo_entry.get().strip()
                    nombre = nombre_entry.get().strip()
                    precio = precio_entry.get().strip()
                    stock = stock_entry.get().strip()
                    
                    if not codigo or not nombre or not precio:
                        messagebox.showerror("Error", "Código, Nombre y Precio son obligatorios")
                        return
                    
                    try:
                        precio = float(precio)
                        if precio <= 0:
                            messagebox.showerror("Error", "Precio debe ser mayor a 0")
                            return
                    except ValueError:
                        messagebox.showerror("Error", "Precio debe ser un número válido")
                        return
                    
                    stock_value = None
                    if stock:
                        if not stock.isdigit():
                            messagebox.showerror("Error", "Stock debe ser un número entero")
                            return
                        stock_value = int(stock)
                        if stock_value < 0:
                            messagebox.showerror("Error", "Stock no puede ser negativo")
                            return
                    
                    conn = sqlite3.connect(self.app.db_path)
                    c = conn.cursor()
                    c.execute("INSERT INTO productos (codigo, nombre, precio, stock) VALUES (?, ?, ?, ?)",
                              (codigo, nombre, precio, stock_value))
                    conn.commit()
                    conn.close()
                    
                    self.actualizar_tabla()
                    ventana.destroy()
                    messagebox.showinfo("Éxito", "Producto agregado correctamente")
                except sqlite3.IntegrityError:
                    messagebox.showerror("Error", "El código ya existe")
                    print("Error: Código duplicado")
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Error al agregar producto: {e}")
                    print(f"Error agregando producto: {e}")
            
            tk.Button(ventana, text="Guardar", command=guardar).grid(row=6, column=0, columnspan=2, pady=10)
            tk.Button(ventana, text="Cancelar", command=ventana.destroy).grid(row=7, column=0, columnspan=2)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir ventana de agregar: {e}")
            print(f"Error abriendo ventana de agregar: {e}")

    def abrir_ventana_editar(self):
        print("Abriendo ventana para editar producto")
        try:
            selected_item = self.tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "Seleccione un producto para editar")
                return
            
            item = self.tree.item(selected_item)
            valores = item["values"]
            producto_id = valores[0]
            
            ventana = Toplevel(self.root)
            ventana.title("Editar Producto")
            ventana.geometry("400x300")
            
            tk.Label(ventana, text="Código").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            codigo_entry = tk.Entry(ventana)
            codigo_entry.grid(row=0, column=1, sticky="w")
            codigo_entry.insert(0, valores[1])
            
            tk.Label(ventana, text="Nombre").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            nombre_entry = tk.Entry(ventana)
            nombre_entry.grid(row=1, column=1, sticky="w")
            nombre_entry.insert(0, valores[2])
            
            tk.Label(ventana, text="Precio (RD$)").grid(row=2, column=0, sticky="w", padx=5, pady=5)
            precio_entry = tk.Entry(ventana)
            precio_entry.grid(row=2, column=1, sticky="w")
            precio_entry.insert(0, valores[3])
            precio_var = tk.DoubleVar(value=float(valores[3]))
            precio_slider = tk.Scale(ventana, from_=0, to=1000, resolution=0.01, orient="horizontal", variable=precio_var, length=200)
            precio_slider.grid(row=3, column=0, columnspan=2, pady=5)
            
            # Sincronizar Entry y Slider para Precio
            def update_precio_entry(*args):
                precio_entry.delete(0, tk.END)
                precio_entry.insert(0, f"{precio_var.get():.2f}")
            def update_precio_slider(event):
                try:
                    precio = float(precio_entry.get())
                    if 0 <= precio <= 1000:
                        precio_var.set(precio)
                    else:
                        messagebox.showerror("Error", "Precio debe estar entre 0 y 1000")
                        precio_entry.delete(0, tk.END)
                        precio_entry.insert(0, f"{precio_var.get():.2f}")
                except ValueError:
                    precio_entry.delete(0, tk.END)
                    precio_entry.insert(0, f"{precio_var.get():.2f}")
            precio_var.trace("w", update_precio_entry)
            precio_entry.bind("<KeyRelease>", update_precio_slider)
            
            tk.Label(ventana, text="Stock (opcional)").grid(row=4, column=0, sticky="w", padx=5, pady=5)
            stock_entry = tk.Entry(ventana)
            stock_entry.grid(row=4, column=1, sticky="w")
            stock_var = tk.IntVar(value=0 if valores[4] == "N/A" else int(valores[4]))
            stock_slider = tk.Scale(ventana, from_=0, to=100, orient="horizontal", variable=stock_var, length=200)
            stock_slider.grid(row=5, column=0, columnspan=2, pady=5)
            if valores[4] != "N/A":
                stock_entry.insert(0, valores[4])
            
            # Sincronizar Entry y Slider para Stock
            def update_stock_entry(*args):
                stock_entry.delete(0, tk.END)
                stock_entry.insert(0, str(stock_var.get()))
            def update_stock_slider(event):
                stock = stock_entry.get().strip()
                if stock:
                    try:
                        stock_value = int(stock)
                        if 0 <= stock_value <= 100:
                            stock_var.set(stock_value)
                        else:
                            messagebox.showerror("Error", "Stock debe estar entre 0 y 100")
                            stock_entry.delete(0, tk.END)
                            stock_entry.insert(0, str(stock_var.get()))
                    except ValueError:
                        stock_entry.delete(0, tk.END)
                        stock_entry.insert(0, str(stock_var.get()))
            stock_var.trace("w", update_stock_entry)
            stock_entry.bind("<KeyRelease>", update_stock_slider)
            
            def guardar():
                print("Guardando cambios de producto")
                try:
                    codigo = codigo_entry.get().strip()
                    nombre = nombre_entry.get().strip()
                    precio = precio_entry.get().strip()
                    stock = stock_entry.get().strip()
                    
                    if not codigo or not nombre or not precio:
                        messagebox.showerror("Error", "Código, Nombre y Precio son obligatorios")
                        return
                    
                    try:
                        precio = float(precio)
                        if precio <= 0:
                            messagebox.showerror("Error", "Precio debe ser mayor a 0")
                            return
                    except ValueError:
                        messagebox.showerror("Error", "Precio debe ser un número válido")
                        return
                    
                    stock_value = None
                    if stock:
                        if not stock.isdigit():
                            messagebox.showerror("Error", "Stock debe ser un número entero")
                            return
                        stock_value = int(stock)
                        if stock_value < 0:
                            messagebox.showerror("Error", "Stock no puede ser negativo")
                            return
                    
                    conn = sqlite3.connect(self.app.db_path)
                    c = conn.cursor()
                    c.execute("UPDATE productos SET codigo = ?, nombre = ?, precio = ?, stock = ? WHERE id = ?",
                              (codigo, nombre, precio, stock_value, producto_id))
                    conn.commit()
                    conn.close()
                    
                    self.actualizar_tabla()
                    ventana.destroy()
                    messagebox.showinfo("Éxito", "Producto editado correctamente")
                except sqlite3.IntegrityError:
                    messagebox.showerror("Error", "El código ya existe")
                    print("Error: Código duplicado")
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Error al editar producto: {e}")
                    print(f"Error editando producto: {e}")
            
            tk.Button(ventana, text="Guardar", command=guardar).grid(row=6, column=0, columnspan=2, pady=10)
            tk.Button(ventana, text="Cancelar", command=ventana.destroy).grid(row=7, column=0, columnspan=2)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir ventana de editar: {e}")
            print(f"Error abriendo ventana de editar: {e}")

    def eliminar_producto(self):
        print("Eliminando producto")
        try:
            selected_item = self.tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "Seleccione un producto para eliminar")
                return
            
            item = self.tree.item(selected_item)
            producto_id = item["values"][0]
            
            conn = sqlite3.connect(self.app.db_path)
            c = conn.cursor()
            c.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
            conn.commit()
            conn.close()
            
            self.actualizar_tabla()
            messagebox.showinfo("Éxito", "Producto eliminado correctamente")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al eliminar producto: {e}")
            print(f"Error eliminando producto: {e}")