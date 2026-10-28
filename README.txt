CONOCE TENANGO - BASE PARA FLASK + MYSQL

1) Instala MySQL Server y MySQL Workbench.
2) En Workbench abre schema.sql y ejecútalo completo.
3) Copia .env.example a un archivo llamado .env y configura la contraseña real de MySQL.
4) Instala Python 3.10 o superior.
5) Abre una terminal dentro de esta carpeta:
   python -m venv venv
   Windows: venv\Scripts\activate
   macOS/Linux: source venv/bin/activate
   pip install -r requirements.txt
6) Ejecuta:
   python app.py
7) Abre http://127.0.0.1:5000
8) Registra una cuenta desde /registro. Las cuentas públicas siempre son usuarios.
9) En Workbench ejecuta la consulta de CREAR_ADMIN.sql usando el correo de la cuenta elegida.
10) Cierra sesión e inicia sesión otra vez. El administrador verá el panel y podrá agregar eventos.
11) Los usuarios normales no verán los enlaces de administración y tampoco podrán abrir esas rutas directamente.

IMPORTANTE:
- Cambia FLASK_SECRET_KEY en .env y no publiques ese archivo.
- Para producción no uses debug=True; usa HTTPS y un servidor WSGI.
- El QR solo abrirá la ficha desde otros dispositivos si la aplicación tiene una URL pública accesible.
- Las compras son registros de demostración. No almacenes números de tarjeta ni proceses pagos reales.
- Este paquete es una base funcional independiente. Para conservar tu mapa original, integra sus enlaces y estilos con las rutas Flask de app.py.
- Si la aplicación se publica, los archivos estáticos deben estar en static/ o ajustarse sus rutas.
