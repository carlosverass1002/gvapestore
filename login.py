import tkinter as tk
from tkinter import messagebox
import sqlite3

class LoginScreen:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=50)
        
        tk.Label(self.frame, text="Gvape Store - Login", font=("Arial", 20)).pack(pady=10)
        
        tk.Label(self.frame, text="Usuario").pack()
        self.entry_usuario = tk.Entry(self.frame)
        self.entry_usuario.pack()
        
        tk.Label(self.frame, text="Contraseña").pack()
        self.entry_contrasena = tk.Entry(self.frame, show="*")
        self.entry_contrasena.pack()
        
        tk.Button(self.frame, text="Iniciar Sesión", command=self.login).pack(pady=20)
    
    def login(self):
        usuario = self.entry_usuario.get()
        contrasena = self.entry_contrasena.get()
        
        conn = sqlite3.connect(self.app.db_path)
        c = conn.cursor()
        c.execute("SELECT rol FROM usuarios WHERE usuario = ? AND contrasena = ?",
                 (usuario, contrasena))
        result = c.fetchone()
        conn.close()
        
        if result:
            self.app.show_main_menu(usuario, result[0])
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")