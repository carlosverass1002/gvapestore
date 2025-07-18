from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.platypus import Image
import os
from datetime import datetime
import traceback
import win32print
import win32api
import time
import subprocess

def generar_factura(venta_id, cliente_nombre, fecha, carrito, subtotal, db_path, usuario_nombre="Desconocido", incluir_cliente=True):
    print(f"Generando recibo para venta_id: {venta_id}")
    try:
        output_dir = "exportaciones/facturas"
        os.makedirs(output_dir, exist_ok=True)
        pdf_path = os.path.join(output_dir, f"recibo_{venta_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        
        receipt_width = 80 * mm
        receipt_height = 297 * mm
        c = canvas.Canvas(pdf_path, pagesize=(receipt_width, receipt_height))
        y = receipt_height - 10 * mm

        # Logo
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=50 * mm, height=15 * mm, hAlign='CENTER')
                logo.drawOn(c, (receipt_width - 50 * mm) / 2, y - 15 * mm)
                y -= 20 * mm
                print(f"Logo incluido en el PDF desde: {logo_path}")
            except Exception as e:
                print(f"Error cargando logo: {e}")
                y -= 10 * mm
        else:
            print(f"Logo no encontrado en la ruta: {logo_path}")
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

        # Imprimir el PDF dos veces con 2 segundos de diferencia
        try:
            imprimir_pdf(pdf_path)  # Primera impresión
            time.sleep(2)  # Esperar 2 segundos
            imprimir_pdf(pdf_path)  # Segunda impresión
        except Exception as e:
            print(f"Error al imprimir con ShellExecute: {e}")
            # Respaldo: Intentar con subprocess y Edge
            try:
                imprimir_pdf_edge(pdf_path)  # Primera impresión
                time.sleep(2)
                imprimir_pdf_edge(pdf_path)  # Segunda impresión
            except Exception as e:
                print(f"Error al imprimir con Edge: {e}")

        return pdf_path

    except Exception as e:
        print(f"Error generando recibo: {e}")
        traceback.print_exc()
        raise

def imprimir_pdf(pdf_path):
    print(f"Imprimiendo PDF con ShellExecute: {pdf_path}")
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"El archivo PDF no existe: {pdf_path}")
        printer_name = win32print.GetDefaultPrinter()
        print(f"Imprimiendo en: {printer_name}")
        
        # Usar win32api.ShellExecute para imprimir el PDF
        win32api.ShellExecute(
            0,
            "print",
            pdf_path,
            f'/d:"{printer_name}"',
            ".",
            0
        )
        print("PDF enviado a la impresora con ShellExecute correctamente")
    except Exception as e:
        print(f"Error en imprimir_pdf: {e}")
        traceback.print_exc()
        raise

def imprimir_pdf_edge(pdf_path):
    print(f"Imprimiendo PDF con Microsoft Edge: {pdf_path}")
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"El archivo PDF no existe: {pdf_path}")
        printer_name = win32print.GetDefaultPrinter()
        print(f"Imprimiendo en: {printer_name}")
        
        # Usar subprocess para llamar a Edge directamente
        edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        if not os.path.exists(edge_path):
            raise FileNotFoundError("Microsoft Edge no encontrado en la ruta predeterminada")
        
        subprocess.run([
            edge_path,
            "--headless",
            f"--print-to-pdf={pdf_path}.temp.pdf",
            f"--printer-name={printer_name}",
            pdf_path
        ], check=True)
        print("PDF enviado a la impresora con Edge correctamente")
    except Exception as e:
        print(f"Error en imprimir_pdf_edge: {e}")
        traceback.print_exc()
        raise