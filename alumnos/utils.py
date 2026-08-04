import qrcode
from io import BytesIO
from django.core.files import File

def generar_qr_alumno(alumno):
    # Genera la imagen del QR con un prefijo y el legajo
    img = qrcode.make(f"ALU-{alumno.legajo}")
    buf = BytesIO()
    img.save(buf, format='PNG')
    
    # Guarda el archivo en el campo ImageField (qr_code) sin hacer commit a la base de datos todavía
    nombre_archivo = f"qr_alumno_{alumno.legajo}.png"
    alumno.qr_code.save(nombre_archivo, File(buf), save=False)