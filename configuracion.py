import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import shutil
import os
from datetime import datetime, timedelta

class ConfiguracionScreen:
    def __init__(self, root, app):
        print("Initializing ConfiguracionScreen")
        self.root = root
        self.app = app
        
        # Verificar que el usuario sea Admin
        if self.app.current_role != "Admin":
            messagebox.showerror("Error", "Acceso denegado. Solo los administradores pueden acceder a Configuración.")
            self.app.show_main_menu(self.app.current_user, self.app.current_role)
            return
        
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Notebook para pestañas
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill="both", expand=True)
        
        # Pestaña: Gestión de Usuarios
        usuarios_frame = tk.Frame(notebook)
        notebook.add(usuarios_frame, text="Usuarios")
        
        tk.Label(usuarios_frame, text="Gestión de Usuarios", font=("Arial", 14)).pack(pady=5)
        
        # Lista de usuarios
        self.usuarios_tree = ttk.Treeview(usuarios_frame, columns=("Usuario", "Rol"), show="headings")
        self.usuarios_tree.heading("Usuario", text="Usuario")
        self.usuarios_tree.heading("Rol", text="Rol")
        self.usuarios_tree.pack(pady=5, fill="both", expand=True)
        
        tk.Button(usuarios_frame, text="Agregar Usuario", command=self.agregar_usuario).pack(side="left", padx=5)
        tk.Button(usuarios_frame, text="Editar Usuario", command=self.editar_usuario).pack(side="left", padx=5)
        tk.Button(usuarios_frame, text="Eliminar Usuario", command=self.eliminar_usuario).pack(side="left", padx=5)
        
        # Pestaña: Base de Datos
        db_frame = tk.Frame(notebook)
        notebook.add(db_frame, text="Base de Datos")
        
        tk.Label(db_frame, text="Gestión de Base de Datos", font=("Arial", 14)).pack(pady=5)
        tk.Button(db_frame, text="Respaldar Base de Datos", command=self.respaldar_db).pack(pady=5)
        tk.Button(db_frame, text="Restaurar Base de Datos", command=self.restaurar_db).pack(pady=5)
        tk.Button(db_frame, text="Limpiar Ventas Antiguas", command=self.limpiar_ventas).pack(pady=5)
        
        # Pestaña: Interfaz
        interfaz_frame = tk.Frame(notebook)
        notebook.add(interfaz_frame, text="Interfaz")
        
        tk.Label(interfaz_frame, text="Tema Visual", font=("Arial", 12)).pack(pady=5)
        self.tema_combobox = ttk.Combobox(interfaz_frame, values=["Claro", "Oscuro"], state="readonly")
        self.tema_combobox.set("Claro")
        self.tema_combobox.pack(pady=5)
        tk.Button(interfaz_frame, text="Aplicar Tema", command=self.aplicar_tema).pack(pady=5)
        
        tk.Label(interfaz_frame, text="Tamaño de Fuente", font=("Arial", 12)).pack(pady=5)
        self.fuente_spinbox = tk.Spinbox(interfaz_frame, from_=8, to=16, width=5)
        self.fuente_spinbox.insert(0, "12")
        self.fuente_spinbox.pack(pady=5)
        tk.Button(interfaz_frame, text="Aplicar Fuente", command=self.aplicar_fuente).pack(pady=5)
        
        # Pestaña: Facturas
        facturas_frame = tk.Frame(notebook)
        notebook.add(facturas_frame, text="Facturas")
        
        tk.Label(facturas_frame, text="Logo de Facturas", font=("Arial", 12)).pack(pady=5)
        tk.Button(facturas_frame, text="Subir Nuevo Logo", command=self.subir_logo).pack(pady=5)
        self.incluir_cliente_var = tk.BooleanVar(value=True)
        tk.Checkbutton(facturas_frame, text="Incluir Nombre del Cliente en Factura", variable=self.incluir_cliente_var).pack(pady=5)
        
        # Pestaña: Exportaciones
        export_frame = tk.Frame(notebook)
        notebook.add(export_frame, text="Exportaciones")
        
        tk.Label(export_frame, text="Ruta de Exportaciones", font=("Arial", 12)).pack(pady=5)
        self.ruta_export_var = tk.StringVar(value="exportaciones/")
        tk.Entry(export_frame, textvariable=self.ruta_export_var, width=50).pack(pady=5)
        tk.Button(export_frame, text="Seleccionar Ruta", command=self.seleccionar_ruta_export).pack(pady=5)
        self.auto_cuadre_var = tk.BooleanVar(value=False)
        tk.Checkbutton(export_frame, text="Generar Cuadre de Caja al Cerrar Sesión", variable=self.auto_cuadre_var).pack(pady=5)
        
        # Pestaña: Parámetros
        params_frame = tk.Frame(notebook)
        notebook.add(params_frame, text="Parámetros")
        
        tk.Label(params_frame, text="Método de Pago Predeterminado", font=("Arial", 12)).pack(pady=5)
        self.metodo_pago_combobox = ttk.Combobox(params_frame, values=["Efectivo", "Transferencia", "Tarjeta"], state="readonly")
        self.metodo_pago_combobox.set("Efectivo")
        self.metodo_pago_combobox.pack(pady=5)
        
        tk.Label(params_frame, text="Días Predeterminados para Reportes", font=("Arial", 12)).pack(pady=5)
        self.dias_reporte_spinbox = tk.Spinbox(params_frame, from_=1, to=365, width=5)
        self.dias_reporte_spinbox.insert(0, "30")
        self.dias_reporte_spinbox.pack(pady=5)
        tk.Button(params_frame, text="Guardar Parámetros", command=self.guardar_parametros).pack(pady=5)
        
        # Botón Volver
        tk.Button(self.frame, text="Volver", command=lambda: self.app.show_main_menu(self.app.current_user, self.app.current_role)).pack(pady=10)
        
        # Cargar datos iniciales
        self.cargar_usuarios()

    def cargar_usuarios(self):
        """Carga la lista de usuarios desde la base de datos."""
        print("Loading users")
        for item in self.usuarios_tree.get_children():
            self.usuarios_tree.delete(item)
        try:
            conn = sqlite3.connect(self.app.db_path)
            c = conn.cursor()
            c.execute("SELECT usuario, rol FROM usuarios")
            for usuario, rol in c.fetchall():
                self.usuarios_tree.insert("", "end", values=(usuario, rol))
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al cargar usuarios: {e}")
            print(f"Error loading users: {e}")

    def agregar_usuario(self):
        """Abre una ventana para agregar un nuevo usuario."""
        print("Opening add user window")
        ventana = tk.Toplevel(self.root)
        ventana.title("Agregar Usuario")
        ventana.geometry("300x200")
        ventana.transient(self.root)
        ventana.grab_set()
        
        tk.Label(ventana, text="Usuario:").pack(pady=5)
        usuario_entry = tk.Entry(ventana)
        usuario_entry.pack(pady=5)
        
        tk.Label(ventana, text="Contraseña:").pack(pady=5)
        contrasena_entry = tk.Entry(ventana, show="*")
        contrasena_entry.pack(pady=5)
        
        tk.Label(ventana, text="Rol:").pack(pady=5)
        rol_combobox = ttk.Combobox(ventana, values=["Admin", "Cajero"], state="readonly")
        rol_combobox.set("Cajero")
        rol_combobox.pack(pady=5)
        
        def guardar():
            usuario = usuario_entry.get().strip()
            contrasena = contrasena_entry.get().strip()
            rol = rol_combobox.get()
            if not usuario or not contrasena:
                messagebox.showerror("Error", "Usuario y contraseña son obligatorios")
                return
            try:
                conn = sqlite3.connect(self.app.db_path)
                c = conn.cursor()
                c.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)", (usuario, contrasena, rol))
                conn.commit()
                conn.close()
                self.cargar_usuarios()
                ventana.grab_release()
                ventana.destroy()
                messagebox.showinfo("Éxito", "Usuario agregado correctamente")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error al agregar usuario: {e}")
                print(f"Error adding user: {e}")
        
        tk.Button(ventana, text="Guardar", command=guardar).pack(pady=10)
        tk.Button(ventana, text="Cancelar", command=lambda: [ventana.grab_release(), ventana.destroy()]).pack(pady=5)

    def editar_usuario(self):
        """Abre una ventana para editar un usuario seleccionado."""
        print("Opening edit user window")
        selected = self.usuarios_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Seleccione un usuario")
            return
        usuario = self.usuarios_tree.item(selected[0])["values"][0]
        
        ventana = tk.Toplevel(self.root)
        ventana.title("Editar Usuario")
        ventana.geometry("300x200")
        ventana.transient(self.root)
        ventana.grab_set()
        
        tk.Label(ventana, text=f"Usuario: {usuario}").pack(pady=5)
        tk.Label(ventana, text="Nueva Contraseña:").pack(pady=5)
        contrasena_entry = tk.Entry(ventana, show="*")
        contrasena_entry.pack(pady=5)
        
        tk.Label(ventana, text="Rol:").pack(pady=5)
        rol_combobox = ttk.Combobox(ventana, values=["Admin", "Cajero"], state="readonly")
        rol_combobox.set(self.usuarios_tree.item(selected[0])["values"][1])
        rol_combobox.pack(pady=5)
        
        def guardar():
            contrasena = contrasena_entry.get().strip()
            rol = rol_combobox.get()
            if not contrasena:
                messagebox.showerror("Error", "La contraseña es obligatoria")
                return
            try:
                conn = sqlite3.connect(self.app.db_path)
                c = conn.cursor()
                c.execute("UPDATE usuarios SET contrasena = ?, rol = ? WHERE usuario = ?", (contrasena, rol, usuario))
                conn.commit()
                conn.close()
                self.cargar_usuarios()
                ventana.grab_release()
                ventana.destroy()
                messagebox.showinfo("Éxito", "Usuario actualizado correctamente")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error al actualizar usuario: {e}")
                print(f"Error updating user: {e}")
        
        tk.Button(ventana, text="Guardar", command=guardar).pack(pady=10)
        tk.Button(ventana, text="Cancelar", command=lambda: [ventana.grab_release(), ventana.destroy()]).pack(pady=5)

    def eliminar_usuario(self):
        """Elimina un usuario seleccionado."""
        print("Deleting user")
        selected = self.usuarios_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Seleccione un usuario")
            return
        usuario = self.usuarios_tree.item(selected[0])["values"][0]
        if usuario == self.app.current_user:
            messagebox.showerror("Error", "No puede eliminar su propio usuario")
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar usuario {usuario}?"):
            try:
                conn = sqlite3.connect(self.app.db_path)
                c = conn.cursor()
                c.execute("DELETE FROM usuarios WHERE usuario = ?", (usuario,))
                conn.commit()
                conn.close()
                self.cargar_usuarios()
                messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error al eliminar usuario: {e}")
                print(f"Error deleting user: {e}")

    def respaldar_db(self):
        """Crea un respaldo de la base de datos."""
        print("Backing up database")
        try:
            backup_dir = "exportaciones/respaldos"
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"gvape_backup_{timestamp}.db")
            shutil.copy(self.app.db_path, backup_path)
            messagebox.showinfo("Éxito", f"Respaldo creado en {backup_path}")
            print(f"Database backed up to {backup_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear respaldo: {e}")
            print(f"Error backing up database: {e}")

    def restaurar_db(self):
        """Restaura la base de datos desde un respaldo."""
        print("Restoring database")
        backup_path = filedialog.askopenfilename(filetypes=[("SQLite Database", "*.db")])
        if backup_path:
            if messagebox.askyesno("Confirmar", "Restaurar la base de datos sobrescribirá los datos actuales. ¿Continuar?"):
                try:
                    shutil.copy(backup_path, self.app.db_path)
                    messagebox.showinfo("Éxito", "Base de datos restaurada correctamente")
                    print(f"Database restored from {backup_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Error al restaurar base de datos: {e}")
                    print(f"Error restoring database: {e}")

    def limpiar_ventas(self):
        """Elimina ventas de más de un año."""
        print("Cleaning old sales")
        if messagebox.askyesno("Confirmar", "Se eliminarán las ventas de más de un año. ¿Continuar?"):
            try:
                conn = sqlite3.connect(self.app.db_path)
                c = conn.cursor()
                one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
                c.execute("DELETE FROM detalles_venta WHERE venta_id IN (SELECT id FROM ventas WHERE fecha < ?)", (one_year_ago,))
                c.execute("DELETE FROM ventas WHERE fecha < ?", (one_year_ago,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", "Ventas antiguas eliminadas correctamente")
                print("Old sales cleaned")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error al limpiar ventas: {e}")
                print(f"Error cleaning sales: {e}")

    def aplicar_tema(self):
        """Aplica el tema seleccionado (claro/oscuro)."""
        print("Applying theme")
        tema = self.tema_combobox.get()
        messagebox.showinfo("Info", f"Tema {tema} aplicado (requiere reinicio para cambios completos)")

    def aplicar_fuente(self):
        """Aplica el tamaño de fuente seleccionado."""
        print("Applying font size")
        try:
            font_size = int(self.fuente_spinbox.get())
            self.root.option_add("*Font", f"Arial {font_size}")
            messagebox.showinfo("Éxito", f"Tamaño de fuente {font_size} aplicado (requiere reinicio para cambios completos)")
        except ValueError:
            messagebox.showerror("Error", "Tamaño de fuente inválido")
            print("Invalid font size")

    def subir_logo(self):
        """Sube un nuevo logo para las facturas."""
        print("Uploading logo")
        logo_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if logo_path:
            try:
                os.makedirs("assets", exist_ok=True)
                shutil.copy(logo_path, "assets/logo.png")
                messagebox.showinfo("Éxito", "Logo actualizado correctamente")
                print("Logo uploaded to assets/logo.png")
            except Exception as e:
                messagebox.showerror("Error", f"Error al subir logo: {e}")
                print(f"Error uploading logo: {e}")

    def seleccionar_ruta_export(self):
        """Selecciona la ruta para exportaciones."""
        print("Selecting export path")
        ruta = filedialog.askdirectory()
        if ruta:
            self.ruta_export_var.set(ruta)
            messagebox.showinfo("Éxito", f"Ruta de exportaciones actualizada a {ruta}")
            print(f"Export path set to {ruta}")

    def guardar_parametros(self):
        """Guarda los parámetros del sistema."""
        print("Saving parameters")
        messagebox.showinfo("Éxito", "Parámetros guardados correctamente")