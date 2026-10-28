import qrcode
datos="https://juegos.games/"
qr=qrcode.make(datos)
qr.save("codigo_qr.png")
print("Código QR generado correctamente")