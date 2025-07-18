import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
import sqlite3

class ClientesScreen:
    def __init__(self, root, app):
        print("Inicializando ClientesScreen")
        self.root = root
        self.app = app
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Tabla de clientes
        self.tree = ttk.Treeview(self.frame, columns=("ID", "Nombre", "Cédula", "Teléfono"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Cédula", text="Cédula")
        self.tree.heading("Teléfono", text="Teléfono")
        self.tree.column("ID", width=50)
        self.tree.column("Nombre", width=200)
        self.tree.column("Cédula", width=100)
        self.tree.column("Teléfono", width=100)
        self.tree.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Botones de acción
        tk.Button(self.frame, text="Agregar Cliente", command=self.abrir_ventana_agregar).grid(row=1, column=0, columnspan=2, pady=5)
        tk.Button(self.frame, text="Editar Cliente", command=self.abrir_ventana_editar).grid(row=2, column=0, columnspan=2, pady=5)
        tk.Button(self.frame, text="Eliminar Cliente", command=self.eliminar_cliente).grid(row=3, column=0, columnspan=2, pady=5)
        tk.Button(self.frame, text="Volver", command=lambda: self.app.show_main_menu(self.app.current_user, self.app.current_role)).grid(row=4, column=0, columnspan=2, pady=5)
        
        self.actualizar_tabla()

    def actualizar_tabla(self):
        print("Actualizando tabla de clientes")
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            conn = sqlite3.connect(self.app.db_path)
            c = conn.cursor()
            c.execute("SELECT id, nombre, cedula, telefono FROM clientes")
            for row in c.fetchall():
                self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3]))
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al actualizar tabla: {e}")
            print(f"Error actualizando tabla: {e}")

    def abrir_ventana_agregar(self):
        print("Abriendo ventana para agregar cliente")
        try:
            ventana = Toplevel(self.root)
            ventana.title("Agregar Cliente")
            ventana.geometry("300x200")
            
            tk.Label(ventana, text="Nombre").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            nombre_entry = tk.Entry(ventana)
            nombre_entry.grid(row=0, column=1, sticky="w")
            
            tk.Label(ventana, text="Cédula").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            cedula_entry = tk.Entry(ventana)
            cedula_entry.grid(row=1, column=1, sticky="w")
            
            tk.Label(ventana, text="Teléfono").grid(row=2, column=0, sticky="w", padx=5, pady=5)
            telefono_entry = tk.Entry(ventana)
            telefono_entry.grid(row=2, column=1, sticky="w")
            
            def guardar():
                print("Guardando nuevo cliente")
                try:
                    nombre = nombre_entry.get().strip()
                    cedula = cedula_entry.get().strip()
                    telefono = telefono_entry.get().strip()
                    
                    if not nombre or not cedula:
                        messagebox.showerror("Error", "Nombre y Cédula son obligatorios")
                        return
                    
                    conn = sqlite3.connect(self.app.db_path)
                    c = conn.cursor()
                    c.execute("INSERT INTO clientes (nombre, cedula, telefono) VALUES (?, ?, ?)",
                              (nombre, cedula, telefono))
                    conn.commit()
                    conn.close()
                    
                    self.actualizar_tabla()
                    ventana.destroy()
                    messagebox.showinfo("Éxito", "Cliente agregado correctamente")
                except sqlite3.IntegrityError:
                    messagebox.showerror("Error", "La cédula ya existe")
                    print("Error: Cédula duplicada")
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Error al agregar cliente: {e}")
                    print(f"Error agregando cliente: {e}")
            
            tk.Button(ventana, text="Guardar", command=guardar).grid(row=3, column=0, columnspan=2, pady=10)
            tk.Button(ventana, text="Cancelar", command=ventana.destroy).grid(row=4, column=0, columnspan=2)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir ventana de agregar: {e}")
            print(f"Error abriendo ventana de agregar: {e}")

    def abrir_ventana_editar(self):
        print("Abriendo ventana para editar cliente")
        try:
            selected_item = self.tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "Seleccione un cliente para editar")
                return
            
            item = self.tree.item(selected_item)
            valores = item["values"]
            cliente_id = valores[0]
            
            ventana = Toplevel(self.root)
            ventana.title("Editar Cliente")
            ventana.geometry("300x200")
            
            tk.Label(ventana, text="Nombre").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            nombre_entry = tk.Entry(ventana)
            nombre_entry.grid(row=0, column=1, sticky="w")
            nombre_entry.insert(0, valores[1])
            
            tk.Label(ventana, text="Cédula").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            cedula_entry = tk.Entry(ventana)
            cedula_entry.grid(row=1, column=1, sticky="w")
            cedula_entry.insert(0, valores[2])
            
            tk.Label(ventana, text="Teléfono").grid(row=2, column=0, sticky="w", padx=5, pady=5)
            telefono_entry = tk.Entry(ventana)
            telefono_entry.grid(row=2, column=1, sticky="w")
            telefono_entry.insert(0, valores[3])
            
            def guardar():
                print("Guardando cambios de cliente")
                try:
                    nombre = nombre_entry.get().strip()
                    cedula = cedula_entry.get().strip()
                    telefono = telefono_entry.get().strip()
                    
                    if not nombre or not cedula:
                        messagebox.showerror("Error", "Nombre y Cédula son obligatorios")
                        return
                    
                    conn = sqlite3.connect(self.app.db_path)
                    c = conn.cursor()
                    c.execute("UPDATE clientes SET nombre = ?, cedula = ?, telefono = ? WHERE id = ?",
                              (nombre, cedula, telefono, cliente_id))
                    conn.commit()
                    conn.close()
                    
                    self.actualizar_tabla()
                    ventana.destroy()
                    messagebox.showinfo("Éxito", "Cliente editado correctamente")
                except sqlite3.IntegrityError:
                    messagebox.showerror("Error", "La cédula ya existe")
                    print("Error: Cédula duplicada")
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Error al editar cliente: {e}")
                    print(f"Error editando cliente: {e}")
            
            tk.Button(ventana, text="Guardar", command=guardar).grid(row=3, column=0, columnspan=2, pady=10)
            tk.Button(ventana, text="Cancelar", command=ventana.destroy).grid(row=4, column=0, columnspan=2)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir ventana de editar: {e}")
            print(f"Error abriendo ventana de editar: {e}")

    def eliminar_cliente(self):
        print("Eliminando cliente")
        try:
            selected_item = self.tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "Seleccione un cliente para eliminar")
                return
            
            item = self.tree.item(selected_item)
            cliente_id = item["values"][0]
            
            # Verificar si el cliente tiene ventas asociadas
            conn = sqlite3.connect(self.app.db_path)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM ventas WHERE cliente_id = ?", (cliente_id,))
            if c.fetchone()[0] > 0:
                messagebox.showerror("Error", "No se puede eliminar el cliente porque tiene ventas asociadas")
                conn.close()
                return
            
            c.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
            conn.commit()
            conn.close()
            
            self.actualizar_tabla()
            messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al eliminar cliente: {e}")
            print(f"Error eliminando cliente: {e}")