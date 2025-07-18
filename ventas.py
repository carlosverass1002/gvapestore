import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
import sqlite3
from datetime import datetime
from factura import generar_factura

class VentasScreen:
    def __init__(self, root, app):
        print("Inicializando VentasScreen")
        self.root = root
        self.app = app
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10, padx=10, fill="both", expand=True)
        self.carrito = []
        self.selected_product = None
        
        # Selección de cliente
        tk.Label(self.frame, text="Seleccionar Cliente").grid(row=0, column=0, sticky="w")
        self.cliente_combobox = ttk.Combobox(self.frame, state="readonly")
        self.cliente_combobox.grid(row=0, column=1, sticky="w")
        self.cliente_combobox["values"] = self.get_clientes()
        
        # Selección de producto
        tk.Label(self.frame, text="Producto").grid(row=1, column=0, sticky="w")
        self.producto_label = tk.Label(self.frame, text="Ningún producto seleccionado")
        self.producto_label.grid(row=1, column=1, sticky="w")
        tk.Button(self.frame, text="Seleccionar Producto", command=self.abrir_ventana_productos).grid(row=1, column=2, padx=5)
        
        # Cantidad
        tk.Label(self.frame, text="Cantidad").grid(row=2, column=0, sticky="w")
        self.cantidad_entry = tk.Entry(self.frame, width=5)
        self.cantidad_entry.grid(row=2, column=1, sticky="w")
        self.cantidad_entry.insert(0, "1")
        self.cantidad_var = tk.IntVar(value=1)
        cantidad_slider = tk.Scale(self.frame, from_=1, to=100, orient="horizontal", variable=self.cantidad_var, length=150)
        cantidad_slider.grid(row=3, column=1, sticky="w", pady=5)
        
        # Sincronizar Entry y Slider para Cantidad
        def update_cantidad_entry(*args):
            self.cantidad_entry.delete(0, tk.END)
            self.cantidad_entry.insert(0, str(self.cantidad_var.get()))
        def update_cantidad_slider(event):
            cantidad = self.cantidad_entry.get().strip()
            if cantidad:
                try:
                    cantidad_value = int(cantidad)
                    if 1 <= cantidad_value <= 100:
                        self.cantidad_var.set(cantidad_value)
                    else:
                        messagebox.showerror("Error", "Cantidad debe estar entre 1 y 100")
                        self.cantidad_entry.delete(0, tk.END)
                        self.cantidad_entry.insert(0, str(self.cantidad_var.get()))
                except ValueError:
                    self.cantidad_entry.delete(0, tk.END)
                    self.cantidad_entry.insert(0, str(self.cantidad_var.get()))
        self.cantidad_var.trace("w", update_cantidad_entry)
        self.cantidad_entry.bind("<KeyRelease>", update_cantidad_slider)
        
        tk.Button(self.frame, text="Agregar al Carrito", command=self.agregar_al_carrito).grid(row=4, column=0, columnspan=3, pady=10)
        
        # Tabla del carrito
        self.tree = ttk.Treeview(self.frame, columns=("Producto", "Cantidad", "Precio", "Total"), show="headings")
        self.tree.heading("Producto", text="Producto")
        self.tree.heading("Cantidad", text="Cantidad")
        self.tree.heading("Precio", text="Precio Unitario")
        self.tree.heading("Total", text="Total")
        self.tree.grid(row=5, column=0, columnspan=3, pady=10)
        
        # Subtotal
        self.subtotal_var = tk.StringVar(value="Subtotal: RD$0.00")
        tk.Label(self.frame, textvariable=self.subtotal_var).grid(row=6, column=0, columnspan=3)
        
        # Dinero recibido y cambio
        tk.Label(self.frame, text="Dinero Recibido (RD$)").grid(row=7, column=0, sticky="w")
        self.dinero_entry = tk.Entry(self.frame, width=10)
        self.dinero_entry.grid(row=7, column=1, sticky="w")
        self.dinero_entry.bind("<KeyRelease>", self.calcular_cambio)
        
        self.cambio_var = tk.StringVar(value="Cambio: RD$0.00")
        tk.Label(self.frame, textvariable=self.cambio_var).grid(row=7, column=2, sticky="w")
        
        # Método de pago
        tk.Label(self.frame, text="Método de Pago").grid(row=8, column=0, sticky="w")
        self.metodo_pago = ttk.Combobox(self.frame, values=["Efectivo", "Transferencia", "Tarjeta"], state="readonly")
        self.metodo_pago.grid(row=8, column=1)
        self.metodo_pago.set("Efectivo")
        
        # Botones de acción
        tk.Button(self.frame, text="Finalizar Venta", command=self.finalizar_venta).grid(row=9, column=0, columnspan=3, pady=10)
        tk.Button(self.frame, text="Volver", command=lambda: self.app.show_main_menu(self.app.current_user, self.app.current_role)).grid(row=10, column=0, columnspan=3)

    def get_clientes(self):
        print("Cargando clientes")
        try:
            conn = sqlite3.connect(self.app.db_path)
            c = conn.cursor()
            c.execute("SELECT nombre FROM clientes")
            clientes = ["Sin Cliente"] + [row[0] for row in c.fetchall()]
            conn.close()
            return clientes
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al cargar clientes: {e}")
            print(f"Error cargando clientes: {e}")
            return ["Sin Cliente"]

    def get_productos(self):
        print("Cargando productos")
        try:
            conn = sqlite3.connect(self.app.db_path)
            c = conn.cursor()
            c.execute("SELECT id, nombre, stock, precio FROM productos")
            productos = c.fetchall()
            conn.close()
            return productos
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al cargar productos: {e}")
            print(f"Error cargando productos: {e}")
            return []

    def abrir_ventana_productos(self):
        print("Abriendo ventana de productos")
        try:
            ventana = Toplevel(self.root)
            ventana.title("Seleccionar Producto")
            ventana.geometry("500x400")
            
            tree = ttk.Treeview(ventana, columns=("ID", "Nombre", "Stock", "Precio"), show="headings")
            tree.heading("ID", text="ID")
            tree.heading("Nombre", text="Nombre")
            tree.heading("Stock", text="Stock")
            tree.heading("Precio", text="Precio (RD$)")
            tree.column("ID", width=50)
            tree.column("Nombre", width=200)
            tree.column("Stock", width=80)
            tree.column("Precio", width=100)
            tree.pack(pady=10, padx=10, fill="both", expand=True)
            
            productos = self.get_productos()
            for prod in productos:
                stock_display = str(prod[2]) if prod[2] is not None else "N/A"
                # Almacenar precio como float
                tree.insert("", "end", values=(prod[0], prod[1], stock_display, float(prod[3])))
            
            def seleccionar_producto(event=None):
                selected_item = tree.selection()
                if selected_item:
                    item = tree.item(selected_item)
                    # Convertir precio a float explícitamente
                    self.selected_product = (
                        item["values"][0],  # ID
                        item["values"][1],  # Nombre
                        None if item["values"][2] == "N/A" else int(item["values"][2]),  # Stock
                        float(item["values"][3])  # Precio
                    )
                    self.producto_label.config(text=self.selected_product[1])
                    ventana.destroy()
            
            tree.bind("<Double-1>", seleccionar_producto)
            tk.Button(ventana, text="Seleccionar", command=seleccionar_producto).pack(pady=5)
            tk.Button(ventana, text="Cancelar", command=ventana.destroy).pack(pady=5)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir ventana de productos: {e}")
            print(f"Error abriendo ventana de productos: {e}")

    def agregar_al_carrito(self):
        print("Agregando al carrito")
        try:
            if not self.selected_product:
                messagebox.showerror("Error", "Seleccione un producto")
                return
            cantidad = self.cantidad_entry.get()
            if not cantidad.isdigit():
                messagebox.showerror("Error", "Cantidad debe ser un número entero")
                return
            cantidad = int(cantidad)
            if cantidad <= 0:
                messagebox.showerror("Error", "Cantidad debe ser mayor a 0")
                return
            
            producto_id, nombre, stock, precio = self.selected_product
            if stock is not None and cantidad > stock:
                messagebox.showerror("Error", f"Stock insuficiente: {stock} unidades disponibles")
                return
            
            total = precio * cantidad
            self.carrito.append({
                "producto_id": producto_id,
                "nombre": nombre,
                "cantidad": cantidad,
                "precio": precio,
                "total": total
            })
            self.actualizar_carrito()
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar al carrito: {e}")
            print(f"Error agregando al carrito: {e}")

    def actualizar_carrito(self):
        print("Actualizando carrito")
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            subtotal = 0
            for item in self.carrito:
                self.tree.insert("", "end", values=(
                    item["nombre"],
                    item["cantidad"],
                    f"RD${item['precio']:.2f}",
                    f"RD${item['total']:.2f}"
                ))
                subtotal += item["total"]
            self.subtotal_var.set(f"Subtotal: RD${subtotal:.2f}")
            self.calcular_cambio()
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar carrito: {e}")
            print(f"Error actualizando carrito: {e}")

    def calcular_cambio(self, event=None):
        print("Calculando cambio")
        try:
            dinero_recibido = float(self.dinero_entry.get() or 0)
            subtotal = sum(item["total"] for item in self.carrito)
            cambio = dinero_recibido - subtotal
            self.cambio_var.set(f"Cambio: RD${cambio:.2f}")
        except ValueError:
            self.cambio_var.set("Cambio: RD$0.00")

    def finalizar_venta(self):
        print("Finalizando venta")
        if not self.carrito:
            messagebox.showerror("Error", "El carrito está vacío")
            return
        try:
            conn = sqlite3.connect(self.app.db_path)
            c = conn.cursor()
            
            # Obtener cliente_id
            cliente_nombre = self.cliente_combobox.get()
            cliente_id = None
            if cliente_nombre != "Sin Cliente":
                c.execute("SELECT id FROM clientes WHERE nombre = ?", (cliente_nombre,))
                cliente_id = c.fetchone()[0]
            
            # Obtener usuario_id
            c.execute("SELECT id FROM usuarios WHERE usuario = ?", (self.app.current_user,))
            usuario_id = c.fetchone()[0]
            
            # Insertar venta
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            subtotal = sum(item["total"] for item in self.carrito)
            metodo_pago = self.metodo_pago.get()
            c.execute(
                "INSERT INTO ventas (fecha, cliente_id, usuario_id, total, metodo_pago) VALUES (?, ?, ?, ?, ?)",
                (fecha, cliente_id, usuario_id, subtotal, metodo_pago)
            )
            venta_id = c.lastrowid
            
            # Insertar detalles de venta y actualizar stock
            for item in self.carrito:
                c.execute(
                    "INSERT INTO detalles_venta (venta_id, producto_id, cantidad, precio_unitario, total) VALUES (?, ?, ?, ?, ?)",
                    (venta_id, item["producto_id"], item["cantidad"], item["precio"], item["total"])
                )
                c.execute("SELECT stock FROM productos WHERE id = ?", (item["producto_id"],))
                stock = c.fetchone()[0]
                if stock is not None:
                    c.execute("UPDATE productos SET stock = stock - ? WHERE id = ?",
                              (item["cantidad"], item["producto_id"]))
            
            conn.commit()
            
            # Generar factura
            generar_factura(venta_id, cliente_nombre, fecha, self.carrito, subtotal, self.app.db_path, usuario_nombre=self.app.current_user)
            
            conn.close()
            self.carrito = []
            self.dinero_entry.delete(0, tk.END)
            self.cantidad_entry.delete(0, tk.END)
            self.cantidad_entry.insert(0, "1")
            self.cantidad_var.set(1)
            self.actualizar_carrito()
            messagebox.showinfo("Éxito", f"Venta finalizada. Factura generada (ID: {venta_id})")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al finalizar venta: {e}")
            print(f"Error finalizando venta: {e}")