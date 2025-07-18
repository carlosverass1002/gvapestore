first release

run in powershell:
pip install pyinstaller



then  run:
pip install tkinter reportlab pandas openpyxl tkcalendar


pyinstaller --onefile --name GvapeStore --windowed --hidden-import=tkinter --hidden-import=reportlab --hidden-import=pandas --hidden-import=openpyxl --hidden-import=tkcalendar --hidden-import=win32api --hidden-import=win32print --add-data "assets;assets" --add-data "base_datos;base_datos" --add-data "exportaciones;exportaciones" app.py
then compile with:



note:
base_datos/
exportaciones/
assets/  *(here goes your logo "Logo.png' file for receip)
