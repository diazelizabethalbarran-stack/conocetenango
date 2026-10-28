
import qrcode

direccion = "http://192.168.1.25:5000/mapa"

qr = qrcode.make(direccion)
qr.save("qr_conoce_tenango.png")

print("QR creado correctamente.")
print("Dirección:", direccion)
