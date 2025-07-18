import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def abrir_ventana_usuarios():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    def cargar_usuarios():
        tabla.delete(*tabla.get_children())
        cursor.execute("SELECT id, usuario FROM usuarios")
        for row in cursor.fetchall():
            tabla.insert('', 'end', values=row)

    def agregar_usuario():
        nombre = usuario_entry.get().strip()
        contraseña = contra_entry.get().strip()

        if not nombre or not contraseña:
            messagebox.showwarning("Advertencia", "Debe completar ambos campos")
            return

        try:
            cursor.execute("INSERT INTO usuarios (usuario, contraseña) VALUES (?, ?)", (nombre, contraseña))
            conn.commit()
            cargar_usuarios()
            limpiar_campos()
            messagebox.showinfo("Éxito", "Usuario creado correctamente")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Este usuario ya existe")

    def eliminar_usuario():
        seleccionado = tabla.selection()
        if not seleccionado:
            return

        id_usuario = tabla.item(seleccionado[0])['values'][0]

        if id_usuario == 1:  # Evitar eliminar admin por defecto
            messagebox.showwarning("Advertencia", "No se puede eliminar el administrador por defecto.")
            return

        confirmar = messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este usuario?")
        if confirmar:
            cursor.execute("DELETE FROM usuarios WHERE id=?", (id_usuario,))
            conn.commit()
            cargar_usuarios()

    def limpiar_campos():
        usuario_entry.delete(0, tk.END)
        contra_entry.delete(0, tk.END)

    # --- Ventana ---
    ventana = tk.Toplevel()
    ventana.title("Gestión de Usuarios")
    ventana.geometry("400x350")

    frame = tk.Frame(ventana)
    frame.pack(pady=10)

    tk.Label(frame, text="Nombre de usuario:").grid(row=0, column=0)
    usuario_entry = tk.Entry(frame)
    usuario_entry.grid(row=0, column=1)

    tk.Label(frame, text="Contraseña:").grid(row=1, column=0)
    contra_entry = tk.Entry(frame, show="*")
    contra_entry.grid(row=1, column=1)

    tk.Button(frame, text="Agregar Usuario", command=agregar_usuario).grid(row=2, column=0, columnspan=2, pady=10)

    tabla = ttk.Treeview(ventana, columns=("ID", "Usuario"), show="headings")
    tabla.heading("ID", text="ID")
    tabla.heading("Usuario", text="Usuario")
    tabla.pack(expand=True, fill="both", padx=10, pady=10)

    tk.Button(ventana, text="Eliminar Usuario", command=eliminar_usuario).pack(pady=5)

    cargar_usuarios()