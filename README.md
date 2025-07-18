🟢 GvapeStore — First Release
✅ Requisitos
Instala los paquetes necesarios ejecutando:

bash
Copy
Edit
pip install tkinter reportlab pandas openpyxl tkcalendar
Para compilar la app en Windows (PowerShell):

bash
Copy
Edit
pip install pyinstaller
🛠️ Compilación
Compila la aplicación en un solo archivo ejecutable con:

bash
Copy
Edit
pyinstaller --onefile --name GvapeStore --windowed ^
  --hidden-import=tkinter ^
  --hidden-import=reportlab ^
  --hidden-import=pandas ^
  --hidden-import=openpyxl ^
  --hidden-import=tkcalendar ^
  --hidden-import=win32api ^
  --hidden-import=win32print ^
  --add-data "assets;assets" ^
  --add-data "base_datos;base_datos" ^
  --add-data "exportaciones;exportaciones" ^
  app.py
🔁 Si estás en CMD en lugar de PowerShell, reemplaza ^ por \ o concatena el comando en una línea.

📁 Estructura de carpetas necesaria (colocar en la raíz del proyecto)
base_datos/

exportaciones/

assets/

Aquí debes colocar tu logo como Logo.png (se usará para los recibos)

💡 Nota
Este es el primer release. Comentarios y sugerencias son bienvenidos.
¡Gracias por probar GvapeStore!

¿Quieres que lo prepare también en formato Markdown para GitHub o prefieres algo más informal para Reddit?
