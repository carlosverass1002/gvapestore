first release


then  run:
pip install tkinter reportlab pandas openpyxl tkcalendar



run in powershell:
pip install pyinstaller


then compile with:

pyinstaller --onefile --name GvapeStore --windowed --hidden-import=tkinter --hidden-import=reportlab --hidden-import=pandas --hidden-import=openpyxl --hidden-import=tkcalendar --hidden-import=win32api --hidden-import=win32print --add-data "assets;assets" --add-data "base_datos;base_datos" --add-data "exportaciones;exportaciones" app.py




note:
base_datos/
exportaciones/
assets/  *(here goes your logo "Logo.png' file for receip)
