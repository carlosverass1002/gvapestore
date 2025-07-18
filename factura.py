from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.platypus import Image
import os
from datetime import datetime
import traceback
import sys
import win32api
import win32print
from tkinter import messagebox

def resource_path(relative_path):
    """Obtiene la ruta absoluta para recursos empaquetados con PyInstaller."""
    try:
        # PyInstaller crea un directorio temporal en sys._MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def generar_factura(venta_id, cliente_nombre, fecha, carrito, subtotal, db_path, usuario_nombre="Desconocido", incluir_cliente=True):
    print(f"Generando recibo para venta_id: {venta_id}")
    try:
        output_dir = resource_path("exportaciones/facturas")
        os.makedirs(output_dir, exist_ok=True)
        pdf_path = os.path.join(output_dir, f"recibo_{venta_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        
        receipt_width = 80 * mm
        receipt_height = 297 * mm
        c = canvas.Canvas(pdf_path, pagesize=(receipt_width, receipt_height))
        y = receipt_height - 10 * mm

        # Logo
        logo_path = resource_path("assets/logo.png")
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=60 * mm, height=20 * mm, hAlign='CENTER')
                logo.drawOn(c, (receipt_width - 60 * mm) / 2, y - 20 * mm)
                y -= 25 * mm
            except Exception as e:
                print(f"Error cargando logo: {e}")
                y -= 10 * mm
        else:
            print("Logo no encontrado")
            y -= 10 * mm

        # Datos de la tienda
        c.setFont("Helvetica", 9)
        for line in [
            "AV. Alfonzo Perozo esq. Carretera Palmar",
            "Villa González, S.D.",
            "Tel: 829-543-9642",
            "Instagram: @G_VAPESTORE24"
        ]:
            c.drawCentredString(receipt_width / 2, y, line)
            y -= 4.5 * mm

        y -= 2 * mm
        c.setFont("Helvetica", 8)
        fecha_formatted = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
        c.drawString(5 * mm, y, f"Fecha: {fecha_formatted}")
        y -= 4 * mm
        c.drawString(5 * mm, y, f"Cajero: {usuario_nombre[:25]}")
        y -= 4 * mm

        if incluir_cliente and cliente_nombre != "Sin Cliente":
            c.drawString(5 * mm, y, "-" * 34)
            y -= 4 * mm
            c.drawString(5 * mm, y, f"Cliente: {cliente_nombre[:25]}")
            y -= 4 * mm

        c.drawString(5 * mm, y, "-" * 34)
        y -= 4 * mm

        # Cabecera productos
        c.setFont("Helvetica-Bold", 8)
        c.drawString(5 * mm, y, "Producto")
        c.drawString(40 * mm, y, "Cant.")
        c.drawString(50 * mm, y, "Precio")
        c.drawString(65 * mm, y, "Total")
        y -= 4 * mm
        c.setFont("Helvetica", 8)
        c.drawString(5 * mm, y, "-" * 34)
        y -= 4 * mm

        # Productos
        for item in carrito:
            if y < 30 * mm:
                c.showPage()
                y = receipt_height - 10 * mm
            producto = item.get("nombre", "")
            c.drawString(5 * mm, y, producto[:25])
            c.drawRightString(48 * mm, y, f"{item['cantidad']:>2}")
            c.drawRightString(62 * mm, y, f"{item['precio']:>5.2f}")
            c.drawRightString(75 * mm, y, f"{item['total']:>5.2f}")
            y -= 4 * mm

        c.drawString(5 * mm, y, "-" * 34)
        y -= 4 * mm

        # Total
        c.setFont("Helvetica-Bold", 9)
        c.drawRightString(62 * mm, y, "TOTAL:")
        c.drawRightString(75 * mm, y, f"{subtotal:>6.2f}")
        y -= 6 * mm

        c.setFont("Helvetica", 8)
        c.drawString(5 * mm, y, "-" * 34)
        y -= 8 * mm

        # Footer
        c.setFont("Helvetica", 8)
        c.drawCentredString(receipt_width / 2, y, "¡Vapea con estilo, elige calidad!")
        y -= 4 * mm
        c.drawCentredString(receipt_width / 2, y, "🚫 Venta solo para mayores de 18 años")

        c.save()
        print(f"Recibo guardado en {pdf_path}")

        # Verificar si hay una impresora predeterminada
        try:
            default_printer = win32print.GetDefaultPrinter()
            if not default_printer:
                raise Exception("No se encontró una impresora predeterminada")
        except Exception as e:
            messagebox.showerror("Error de Impresión", f"No se puede imprimir: {e}. Verifique que una impresora esté configurada y encendida.")
            print(f"Error verificando impresora: {e}")
            return pdf_path

        # Enviar a la cola de impresión dos veces
        try:
            for _ in range(2):
                win32api.ShellExecute(0, "print", pdf_path, None, ".", 0)
                print(f"Enviado a la cola de impresión ({_ + 1}/2)")
        except Exception as e:
            messagebox.showerror("Error de Impresión", f"Error al enviar a la cola de impresión: {e}. Verifique que la impresora esté funcionando.")
            print(f"Error al enviar a la cola de impresión: {e}")
            traceback.print_exc()

        return pdf_path

    except Exception as e:
        print(f"Error generando recibo: {e}")
        traceback.print_exc()
        messagebox.showerror("Error", f"Error generando recibo: {e}")
        raise