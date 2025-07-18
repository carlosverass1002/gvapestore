Perfecto, aquí tienes el texto listo para copiar y pegar directamente en Reddit:

---

## 🟢 GvapeStore — First Release

### ✅ Requisitos

Ejecuta este comando para instalar las dependencias necesarias:

```
pip install tkinter reportlab pandas openpyxl tkcalendar
```

En PowerShell, instala PyInstaller:

```
pip install pyinstaller
```

---

### 🛠️ Compilación del ejecutable

Ejecuta este comando para compilar la app:

```
pyinstaller --onefile --name GvapeStore --windowed --hidden-import=tkinter --hidden-import=reportlab --hidden-import=pandas --hidden-import=openpyxl --hidden-import=tkcalendar --hidden-import=win32api --hidden-import=win32print --add-data "assets;assets" --add-data "base_datos;base_datos" --add-data "exportaciones;exportaciones" app.py
```

> Si usas CMD en lugar de PowerShell, reemplaza `^` por `\` o escribe todo en una sola línea.

---

### 📁 Carpetas requeridas en la raíz del proyecto

Asegúrate de tener las siguientes carpetas:

* `base_datos/`
* `exportaciones/`
* `assets/` → Aquí debes colocar tu logo con el nombre exacto: `Logo.png` (se usará en los recibos)

---

### 💬 Nota

Este es el **primer release** de GvapeStore.
Comentarios, pruebas y sugerencias son bienvenidos. ¡Gracias por probarlo!

---

Listo para pegar. Si necesitas otra versión para GitHub o presentación más técnica, solo dime.
