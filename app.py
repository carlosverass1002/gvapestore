import tkinter as tk
from tkinter import messagebox, filedialog
import traceback
import sqlite3
import os

try:
    from login import LoginScreen
    from ventas import VentasScreen
    from productos import ProductosScreen
    from clientes import ClientesScreen
    from reportes import ReportesScreen
    from configuracion import ConfiguracionScreen
except ImportError as e:
    print(f"Error importando módulos: {e}")
    traceback.print_exc()
    messagebox.showerror("Error", f"Error importando módulos: {e}")
    exit(1)

class GvapeStoreApp:
    def __init__(self, root):
        print("Iniciando GvapeStoreApp")
        try:
            self.root = root
            self.root.title("Gvape Store")
            self.root.geometry("800x600")
            self.db_path = "base_datos/gvape.db"
            self.current_user = None
            self.current_role = None
            print("Verificando dependencias")
            self.check_dependencies()
            print("Verificando base de datos")
            self.verify_database()
            print("Intentando mostrar pantalla de login")
            self.show_login()
        except Exception as e:
            print(f"Error en __init__: {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Error inicializando la aplicación: {e}")
            exit(1)

    def check_dependencies(self):
        print("Verificando dependencias")
        try:
            import reportlab
            import pandas
            import openpyxl
            import tkcalendar
            print("Todas las dependencias instaladas")
        except ImportError as e:
            print(f"Falta dependencia: {e}")
            messagebox.showerror("Error", f"Falta una dependencia: {e}. Ejecute 'pip install tkinter reportlab pandas openpyxl tkcalendar'")
            exit(1)

    def verify_database(self):
        print("Verificando existencia de la base de datos")
        try:
            # Verificar si el archivo de la base de datos existe
            if not os.path.exists(self.db_path):
                response = messagebox.askyesno(
                    "Base de datos no encontrada",
                    f"No se encontró la base de datos en {self.db_path}. ¿Desea seleccionar una base de datos existente?",
                    default="yes"
                )
                if response:  # Sí: Seleccionar una base de datos existente
                    self.db_path = filedialog.askopenfilename(
                        title="Seleccionar base de datos",
                        filetypes=[("Archivos SQLite", "*.db")]
                    )
                    if not self.db_path:
                        messagebox.showinfo("Información", "No se seleccionó ninguna base de datos. Se creará una nueva.")
                        self.db_path = "base_datos/gvape.db"
                        os.makedirs("base_datos", exist_ok=True)
                        self.initialize_database()
                    else:
                        print(f"Base de datos seleccionada: {self.db_path}")
                        self.check_database_structure()
                else:  # No: Crear una nueva base de datos
                    os.makedirs("base_datos", exist_ok=True)
                    self.initialize_database()
            else:
                print(f"Base de datos encontrada en {self.db_path}")
                self.check_database_structure()
        except Exception as e:
            print(f"Error verificando base de datos: {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Error verificando base de datos: {e}")
            exit(1)

    def check_database_structure(self):
        print("Verificando estructura de la base de datos")
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            # Verificar y crear tabla usuarios si no existe
            c.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT UNIQUE,
                    contrasena TEXT,
                    rol TEXT
                )
            """)
            # Insertar usuarios iniciales solo si la tabla está vacía
            c.execute("SELECT COUNT(*) FROM usuarios")
            if c.fetchone()[0] == 0:
                c.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)",
                          ("admin", "admin123", "Admin"))
                c.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)",
                          ("cajero", "cajero123", "Cajero"))

            # Verificar y crear tabla clientes si no existe
            c.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT,
                    cedula TEXT,
                    telefono TEXT
                )
            """)

            # Verificar y crear tabla productos si no existe
            c.execute("""
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE,
                    nombre TEXT,
                    precio REAL,
                    stock INTEGER
                )
            """)
            # Insertar productos iniciales solo si la tabla está vacía
            c.execute("SELECT COUNT(*) FROM productos")
            if c.fetchone()[0] == 0:
                c.execute("INSERT INTO productos (codigo, nombre, precio, stock) VALUES (?, ?, ?, ?)",
                          ("00001", "Liquido Fresa", 500.00, 5))
                c.execute("INSERT INTO productos (codigo, nombre, precio, stock) VALUES (?, ?, ?, ?)",
                          ("00002", "Liquido Menta", 500.00, 5))
                c.execute("INSERT INTO productos (codigo, nombre, precio, stock) VALUES (?, ?, ?, ?)",
                          ("00003", "Servicio Limpieza", 200.00, None))

            # Verificar y crear tabla ventas si no existe
            c.execute("""
                CREATE TABLE IF NOT EXISTS ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT,
                    cliente_id INTEGER,
                    usuario_id INTEGER,
                    total REAL,
                    metodo_pago TEXT,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            """)

            # Verificar y crear tabla detalles_venta si no existe
            c.execute("""
                CREATE TABLE IF NOT EXISTS detalles_venta (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venta_id INTEGER,
                    producto_id INTEGER,
                    cantidad INTEGER,
                    precio_unitario REAL,
                    total REAL,
                    FOREIGN KEY (venta_id) REFERENCES ventas(id),
                    FOREIGN KEY (producto_id) REFERENCES productos(id)
                )
            """)
            # Verificar si la columna 'total' existe en detalles_venta
            c.execute("PRAGMA table_info(detalles_venta)")
            columns = [col[1] for col in c.fetchall()]
            if "total" not in columns:
                print("Añadiendo columna 'total' a detalles_venta")
                c.execute("ALTER TABLE detalles_venta ADD COLUMN total REAL")

            conn.commit()
            conn.close()
            print("Estructura de base de datos verificada y completada")
        except sqlite3.Error as e:
            print(f"Error verificando estructura de base de datos: {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Error verificando estructura de base de datos: {e}")
            exit(1)

    def initialize_database(self):
        print("Creando nueva base de datos")
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            # Crear tabla usuarios
            c.execute("""
                CREATE TABLE usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT UNIQUE,
                    contrasena TEXT,
                    rol TEXT
                )
            """)
            c.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)",
                      ("admin", "admin123", "Admin"))
            c.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)",
                      ("cajero", "cajero123", "Cajero"))

            # Crear tabla clientes
            c.execute("""
                CREATE TABLE clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT,
                    cedula TEXT,
                    telefono TEXT
                )
            """)

            # Crear tabla productos
            c.execute("""
                CREATE TABLE productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE,
                    nombre TEXT,
                    precio REAL,
                    stock INTEGER
                )
            """)
            c.execute("INSERT INTO productos (codigo, nombre, precio, stock) VALUES (?, ?, ?, ?)",
                      ("00001", "Liquido Fresa", 500.00, 5))
            c.execute("INSERT INTO productos (codigo, nombre, precio, stock) VALUES (?, ?, ?, ?)",
                      ("00002", "Liquido Menta", 500.00, 5))
            c.execute("INSERT INTO productos (codigo, nombre, precio, stock) VALUES (?, ?, ?, ?)",
                      ("00003", "Servicio Limpieza", 200.00, None))

            # Crear tabla ventas
            c.execute("""
                CREATE TABLE ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT,
                    cliente_id INTEGER,
                    usuario_id INTEGER,
                    total REAL,
                    metodo_pago TEXT,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            """)

            # Crear tabla detalles_venta
            c.execute("""
                CREATE TABLE detalles_venta (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venta_id INTEGER,
                    producto_id INTEGER,
                    cantidad INTEGER,
                    precio_unitario REAL,
                    total REAL,
                    FOREIGN KEY (venta_id) REFERENCES ventas(id),
                    FOREIGN KEY (producto_id) REFERENCES productos(id)
                )
            """)

            conn.commit()
            conn.close()
            print("Base de datos creada e inicializada correctamente")
        except sqlite3.Error as e:
            print(f"Error inicializando base de datos: {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Error inicializando base de datos: {e}")
            exit(1)

    def clear_screen(self):
        print("Limpiando pantalla")
        try:
            for widget in self.root.winfo_children():
                widget.destroy()
        except Exception as e:
            print(f"Error limpiando pantalla: {e}")
            traceback.print_exc()

    def show_login(self):
        print("Mostrando pantalla de login")
        try:
            self.clear_screen()
            LoginScreen(self.root, self)
        except Exception as e:
            print(f"Error mostrando pantalla de login: {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Error mostrando pantalla de login: {e}")

    def show_main_menu(self, user, role):
        print(f"Mostrando menú principal para usuario: {user}, rol: {role}")
        try:
            self.current_user = user
            self.current_role = role
            self.clear_screen()
            
            frame = tk.Frame(self.root)
            frame.pack(pady=20)
            
            tk.Label(frame, text=f"Bienvenido, {user} ({role})", font=("Arial", 16)).pack(pady=10)
            
            button_frame = tk.Frame(frame)
            button_frame.pack()
            
            buttons = [
                ("Vender", lambda: self.show_screen(VentasScreen)),
                ("Clientes", lambda: self.show_screen(ClientesScreen)),
                ("Historial de Ventas", lambda: self.show_screen(lambda root, app: ReportesScreen(root, app, "historial"))),
                ("Reportes", lambda: self.show_screen(lambda root, app: ReportesScreen(root, app, "reportes"))),
                ("Productos", lambda: self.show_screen(ProductosScreen)),
                ("Configuración", lambda: self.show_screen(ConfiguracionScreen)),
                ("Cerrar Sesión", self.show_login)
            ]
            
            # Filtrar botones para cajeros: solo Vender, Clientes, Historial de Ventas, Reportes y Cerrar Sesión
            if self.current_role != "Admin":
                buttons = [btn for btn in buttons if btn[0] in ["Vender", "Clientes", "Historial de Ventas", "Reportes", "Cerrar Sesión"]]
            
            # Organizar botones en una sola fila para cajeros, dos filas para admins
            for i, (text, command) in enumerate(buttons):
                try:
                    if self.current_role == "Admin" and i >= 4:
                        tk.Button(button_frame, text=text, command=command, width=15, height=2).grid(row=1, column=i-4, padx=5, pady=5)
                    else:
                        tk.Button(button_frame, text=text, command=command, width=15, height=2).grid(row=0, column=i, padx=5, pady=5)
                except Exception as e:
                    print(f"Error creando botón {text}: {e}")
                    traceback.print_exc()
        except Exception as e:
            print(f"Error mostrando menú principal: {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Error mostrando menú principal: {e}")

    def show_screen(self, screen_class):
        print(f"Mostrando pantalla: {screen_class.__name__ if hasattr(screen_class, '__name__') else 'ReportesScreen'}")
        try:
            self.clear_screen()
            screen_class(self.root, self)
        except Exception as e:
            print(f"Error mostrando pantalla: {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Error mostrando pantalla: {e}")

if __name__ == "__main__":
    print("Iniciando aplicación")
    try:
        root = tk.Tk()
        app = GvapeStoreApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Error iniciando aplicación: {e}")
        traceback.print_exc()
        messagebox.showerror("Error", f"Error iniciando aplicación: {e}")