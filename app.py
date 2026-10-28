import os
from functools import wraps
from datetime import datetime

import uuid
import io
import base64
import qrcode

import ssl
import mysql.connector
from mysql.connector import Error
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv


load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

DB_CONFIG = {
    'host': os.environ.get('DB_HOST'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'database': os.environ.get('DB_NAME', 'conoce_tenango'),
    'port': int(os.environ.get('DB_PORT', '4000')),
    'ssl_ca': os.path.join(BASE_DIR, 'isrgrootx1 (1).pem'),
    'ssl_verify_cert': True,
    'ssl_verify_identity': True
}

def conectar_db():
    """Abre una conexión segura con TiDB Cloud."""
    return mysql.connector.connect(**DB_CONFIG)



def consulta(sql, valores=(), uno=False):
    """Ejecuta SELECT y devuelve diccionarios; cierra siempre la conexión."""
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(sql, valores)
        return cursor.fetchone() if uno else cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()


def ejecutar(sql, valores=()):
    """Ejecuta INSERT/UPDATE/DELETE y devuelve el id insertado."""
    conexion = conectar_db()
    cursor = conexion.cursor()
    try:
        cursor.execute(sql, valores)
        conexion.commit()
        return cursor.lastrowid
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def requiere_login(vista):
    @wraps(vista)
    def decorada(*args, **kwargs):
        if not session.get('id_usuario'):
            flash('Inicia sesión para continuar.', 'info')
            return redirect(url_for('login'))
        return vista(*args, **kwargs)
    return decorada


def requiere_admin(vista):
    @wraps(vista)
    def decorada(*args, **kwargs):
        if not session.get('id_administrador'):
            flash('Inicia sesión como administrador.', 'info')
            return redirect(url_for('login_admin'))
        return vista(*args, **kwargs)
    return decorada


# INICIO Y MAPA: se renderizan tus HTML originales.
@app.route('/')
@app.route('/index')
def inicio():
    return render_template('index.html')


@app.route('/mapa')
def mapa():
    # Conserva la distribución original de los tres paneles y el carrusel.
    return render_template('mapa.html')


@app.route('/api/lugares')
def api_lugares():
    try:
        lugares = consulta('''SELECT id_lugar, nombre, categoria, descripcion,
                                    direccion, telefono, horario, latitud, longitud
                             FROM lugares ORDER BY id_lugar''')
        return jsonify(lugares)
    except Error as e:
        app.logger.exception('Error al consultar lugares')
        return jsonify({'error': 'No se pudieron cargar los lugares', 'detalle': str(e)}), 500


@app.route('/api/eventos')
def api_eventos():
    try:
        eventos = consulta('''SELECT e.id_evento, e.id_lugar, e.nombre, e.descripcion,
                                     e.fecha, e.hora, e.lugar, e.precio,
                                     l.nombre AS nombre_lugar
                              FROM eventos e
                              LEFT JOIN lugares l ON l.id_lugar = e.id_lugar
                              ORDER BY e.fecha, e.hora''')
        for ev in eventos:
            if ev.get('fecha'):
                ev['fecha'] = ev['fecha'].isoformat()
            if ev.get('hora'):
                ev['hora'] = str(ev['hora'])
            if ev.get('precio') is not None:
                ev['precio'] = float(ev['precio'])
        return jsonify(eventos)
    except Error as e:
        app.logger.exception('Error al consultar eventos')
        return jsonify({'error': 'No se pudieron cargar los eventos', 'detalle': str(e)}), 500


# REGISTRO, INICIO DE SESIÓN Y PERFIL.


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip().lower()
        telefono = request.form.get('telefono', '').strip()
        password = (
            request.form.get('password')
            or request.form.get('contrasena')
            or ''
        )

        if not nombre or not correo or not password:
            flash('Completa nombre, correo y contraseña.', 'error')
            return render_template('registro.html')

        try:
            token_qr = uuid.uuid4().hex

            ejecutar(
                '''
                INSERT INTO usuarios
                    (nombre, correo, telefono, password_hash, rol, qr_token)
                VALUES (%s, %s, %s, %s, 'usuario', %s)
                ''',
                (
                    nombre,
                    correo,
                    telefono or None,
                    generate_password_hash(password),
                    token_qr
                )
            )

            flash('Registro completado. Ahora inicia sesión.', 'success')
            return redirect(url_for('login'))

        except Error:
            app.logger.exception('Error al registrar usuario')
            flash(
                'No se pudo guardar el registro. Revisa la terminal.',
                'error'
            )

    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo', '').strip().lower()
        password = (
            request.form.get('password')
            or request.form.get('contrasena')
            or ''
        )

        try:
            usuario = consulta(
                '''SELECT id_usuario, nombre, correo, telefono,
                          password_hash
                   FROM usuarios
                   WHERE correo = %s AND rol = 'usuario' ''',
                (correo,),
                uno=True
            )

        except Error:
            app.logger.exception('Error al iniciar sesión')
            flash('Error al consultar MySQL.', 'error')
            return render_template('login.html')

        if usuario and check_password_hash(
            usuario['password_hash'], password
        ):
            session.clear()
            session['id_usuario'] = usuario['id_usuario']
            session['nombre'] = usuario['nombre']
            session['correo'] = usuario['correo']
            session['rol'] = 'usuario'
            session['tipo_sesion'] = 'usuario'

            return redirect(url_for('perfil'))

        flash('Correo o contraseña incorrectos.', 'error')

    return render_template('login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        correo = request.form.get('correo', '').strip().lower()
        password = (
            request.form.get('password')
            or request.form.get('contrasena')
            or ''
        )

        try:
            administrador = consulta(
                '''SELECT id_administrador, nombre, correo, password_hash
                   FROM administradores
                   WHERE correo = %s''',
                (correo,),
                uno=True
            )
        except Error:
            app.logger.exception('Error al iniciar sesión de administrador')
            flash('Error al consultar MySQL. Revisa la terminal.', 'error')
            return render_template('login_admin.html')

        if (
            administrador
            and check_password_hash(
                administrador['password_hash'], password
            )
        ):
            session.clear()
            session['id_administrador'] = administrador['id_administrador']
            session['admin_nombre'] = administrador['nombre']
            session['admin_correo'] = administrador['correo']
            session['tipo_sesion'] = 'admin'

            return redirect(url_for('administrar'))

        flash('Correo o contraseña incorrectos.', 'error')

    return render_template('login_admin.html')



@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada.', 'success')
    return redirect(url_for('inicio'))



@app.route('/perfil')
@requiere_login
def perfil():
    usuario = consulta(
        '''
        SELECT id_usuario, nombre, correo, telefono, rol, qr_token
        FROM usuarios
        WHERE id_usuario = %s
        ''',
        (session['id_usuario'],),
        uno=True
    )

    if not usuario:
        session.clear()
        return redirect(url_for('login'))

    # Crear la imagen QR a partir del token personal.
    codigo = qrcode.make(
    url_for(
        'validar_qr_usuario',
        token=usuario['qr_token'],
        _external=True
    )
    )
    memoria = io.BytesIO()
    codigo.save(memoria, format='PNG')

    qr_base64 = base64.b64encode(
        memoria.getvalue()
    ).decode('utf-8')

    # Consultar el saldo actual.
    saldo = consulta(
        '''
        SELECT puntos
        FROM puntos_usuarios
        WHERE id_usuario = %s
        ''',
        (usuario['id_usuario'],),
        uno=True
    )

    if not saldo:
        ejecutar(
            '''
            INSERT IGNORE INTO puntos_usuarios (id_usuario, puntos)
            VALUES (%s, 0)
            ''',
            (usuario['id_usuario'],)
        )
        puntos = 0
    else:
        puntos = saldo['puntos']

    # Historial de visitas del usuario.
    visitas_usuario = consulta(
        '''
        SELECT v.fecha_visita, v.puntos_obtenidos, l.nombre AS nombre_lugar
        FROM visitas v
        JOIN lugares l ON l.id_lugar = v.id_lugar
        WHERE v.id_usuario = %s
        ORDER BY v.fecha_visita DESC
        ''',
        (usuario['id_usuario'],)
    )

    compras_usuario = consulta(
        '''
        SELECT
            c.id_compra,
            e.nombre AS nombre_evento,
            c.cantidad,
            c.total,
            c.estado,
            c.fecha_compra
        FROM compras c
        INNER JOIN eventos e
            ON c.id_evento = e.id_evento
        WHERE c.id_usuario = %s
        ORDER BY c.fecha_compra DESC
        ''',
        (usuario['id_usuario'],)
    )
    
    return render_template(
        'perfil.html',
        usuario=usuario,
        qr_base64=qr_base64,
        puntos=puntos,
        visitas=visitas_usuario,
        compras=compras_usuario
    )


# VALIDAR QR PERSONAL DEL USUARIO
@app.route('/validar-qr-usuario/<token>', methods=['GET', 'POST'])
def validar_qr_usuario(token):
    PUNTOS_POR_VISITA = 10

    # Buscar al visitante mediante el token de su QR
    usuario = consulta("""
        SELECT id_usuario, nombre, qr_token
        FROM usuarios
        WHERE qr_token = %s
    """, (token,), uno=True)

    if not usuario:
        return "El código QR no es válido.", 404

    # El establecimiento debe iniciar sesión en este dispositivo
    id_establecimiento = session.get('id_establecimiento')
    id_lugar = session.get('id_lugar_establecimiento')

    if not id_establecimiento or not id_lugar:
        return """
            <h2>Visitante identificado</h2>
            <p>El QR es válido, pero debes iniciar sesión como
            establecimiento para registrar la visita.</p>
            <a href="/login-establecimiento">
                Iniciar sesión como establecimiento
            </a>
        """

    # Verificar que el establecimiento esté activo y asociado al lugar
    establecimiento = consulta("""
        SELECT id_establecimiento
        FROM establecimientos
        WHERE id_establecimiento = %s
          AND id_lugar = %s
          AND activo = 1
    """, (id_establecimiento, id_lugar), uno=True)

    if not establecimiento:
        session.pop('id_establecimiento', None)
        session.pop('id_lugar_establecimiento', None)
        session.pop('nombre_establecimiento', None)

        return "El establecimiento no está activo o no tiene un lugar válido.", 403

    mensaje = ""

    if request.method == 'POST':
        try:
            # Registrar la visita en MySQL
            ejecutar("""
                INSERT INTO visitas
                    (id_usuario, id_lugar, puntos_obtenidos, fecha_visita)
                VALUES (%s, %s, %s, NOW())
            """, (
                usuario['id_usuario'],
                id_lugar,
                PUNTOS_POR_VISITA
            ))

            # Crear el registro de puntos si el usuario aún no tiene uno
            ejecutar("""
                INSERT IGNORE INTO puntos_usuarios (id_usuario, puntos)
                VALUES (%s, 0)
            """, (usuario['id_usuario'],))

            # Acumular los puntos
            ejecutar("""
                UPDATE puntos_usuarios
                SET puntos = puntos + %s
                WHERE id_usuario = %s
            """, (PUNTOS_POR_VISITA, usuario['id_usuario']))

            return f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport"
                          content="width=device-width, initial-scale=1">
                    <title>Visita registrada</title>
                </head>
                <body>
                    <h2>¡Visita registrada correctamente!</h2>
                    <p>Visitante: {usuario['nombre']}</p>
                    <p>Puntos otorgados: {PUNTOS_POR_VISITA}</p>
                    <p>Los puntos se han agregado a su cuenta.</p>
                </body>
                </html>
            """

        except Exception:
            app.logger.exception("Error al registrar la visita")
            return "No se pudo registrar la visita. Revisa la terminal de Flask.", 500


    return render_template(
        'validar_qr_usuario.html',
        usuario=usuario,
        puntos_por_visita=PUNTOS_POR_VISITA
    )

   

# EVENTOS.
@app.route('/eventos')
def eventos():
    lista = consulta('''SELECT e.*, l.nombre AS nombre_lugar, l.categoria
                        FROM eventos e LEFT JOIN lugares l ON l.id_lugar = e.id_lugar
                        ORDER BY e.fecha, e.hora''')
    return render_template('eventos.html', eventos=lista)


@app.route('/evento/<int:id_evento>')
def evento_detalle(id_evento):
    evento = consulta('''SELECT e.*, l.nombre AS nombre_lugar
                         FROM eventos e LEFT JOIN lugares l ON l.id_lugar = e.id_lugar
                         WHERE e.id_evento = %s''', (id_evento,), uno=True)
    if not evento:
        return 'Evento no encontrado', 404
    return render_template('eventos.html', evento=evento)



# DETALLE DE LUGAR
@app.route("/detalle/<int:id_lugar>")
def detalle(id_lugar):
    # Aquí debes buscar el lugar en MySQL
    # y mostrar su página de detalles.
    return render_template("detalle.html", id_lugar=id_lugar)


# RESERVACIONES
@app.route('/reservar/<int:id_lugar>', methods=['GET', 'POST'])
@app.route('/reservar', methods=['GET', 'POST'])
@requiere_login
def reservar(id_lugar=None):

    if request.method == 'POST':
        print("=== SE RECIBIÓ UNA RESERVACIÓN ===")
        print("DATOS RECIBIDOS:", request.form.to_dict())

        try:
            id_lugar_form = request.form.get('id_lugar') or id_lugar

            nombre = (
                request.form.get('nombre_cliente')
                or session.get('nombre', '')
            ).strip()

            correo = (
                request.form.get('correo')
                or session.get('correo', '')
            ).strip()

            telefono = request.form.get('telefono', '').strip()
            entrada = request.form.get('fecha_entrada', '').strip()
            salida = request.form.get('fecha_salida', '').strip()
            comentarios = request.form.get('comentarios', '').strip()

            personas = int(request.form.get('personas', '1'))
            id_real = int(id_lugar_form)

            print("ID DE USUARIO:", session.get('id_usuario'))
            print("ID DEL LUGAR:", id_real)
            print("FECHA DE ENTRADA:", entrada)
            print("FECHA DE SALIDA:", salida)
            print("PERSONAS:", personas)

            if not all([nombre, correo, telefono, entrada, salida]):
                flash('Completa todos los datos requeridos.', 'error')

            elif not session.get('id_usuario'):
                flash('No se encontró la sesión del usuario. Inicia sesión nuevamente.', 'error')

            elif personas < 1:
                flash('El número de personas debe ser mayor que cero.', 'error')

            elif salida <= entrada:
                flash('La fecha de salida debe ser posterior a la entrada.', 'error')

            else:
                lugar_bd = consulta(
                    'SELECT id_lugar FROM lugares WHERE id_lugar = %s',
                    (id_real,),
                    uno=True
                )

                print("RESULTADO DEL LUGAR:", lugar_bd)

                if not lugar_bd:
                    flash('El lugar seleccionado no existe en MySQL.', 'error')

                else:
                    print("INTENTANDO GUARDAR EN MYSQL...")

                    ejecutar(
                        '''
                        INSERT INTO reservaciones (
                            id_usuario,
                            id_lugar,
                            nombre_cliente,
                            correo,
                            telefono,
                            fecha,
                            fecha_entrada,
                            fecha_salida,
                            personas,
                            comentarios,
                            estado
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pendiente')
                        ''',
                        (
                            session['id_usuario'],
                            id_real,
                            nombre,
                            correo,
                            telefono,
                            entrada + ' 00:00:00',
                            entrada + ' 00:00:00',
                            salida + ' 00:00:00',
                            personas,
                            comentarios or None
                        )
                    )

                    print("RESERVACIÓN GUARDADA CORRECTAMENTE")

                    flash(
                        '¡Tu reservación se guardó correctamente!',
                        'success'
                    )
                    return redirect(url_for('perfil'))

        except (ValueError, TypeError, Error):
            app.logger.exception('ERROR AL GUARDAR LA RESERVACIÓN')
            flash(
                'No se pudo guardar la reservación. Revisa el error en la terminal.',
                'error'
            )

    lugar = None

    if id_lugar is not None:
        lugar = consulta(
            'SELECT * FROM lugares WHERE id_lugar = %s',
            (id_lugar,),
            uno=True
        )

    lugares = consulta(
        '''
        SELECT id_lugar, nombre, categoria
        FROM lugares
        ORDER BY nombre
        '''
    )

    return render_template(
        'reservar.html',
        lugar=lugar,
        lugares=lugares,
        id_lugar=id_lugar
    )


# COMPRAS DE BOLETOS PARA EVENTOS.
@app.route('/comprar/<int:id_evento>', methods=['GET', 'POST'])
@app.route('/comprar', methods=['GET', 'POST'])
@requiere_login
def comprar(id_evento=None):

    eventos_disponibles = consulta("""
        SELECT id_evento, nombre, fecha, precio
        FROM eventos
        ORDER BY fecha, nombre
    """)

    if request.method == 'POST':
        try:
            id_evento_form = int(
                request.form.get('id_evento') or id_evento or 0
            )
            cantidad = int(request.form.get('cantidad', '1'))

            if cantidad < 1 or cantidad > 20:
                flash('Selecciona entre 1 y 20 boletos.', 'error')
                return redirect(url_for('comprar'))

            evento = consulta("""
                SELECT id_evento, nombre, precio
                FROM eventos
                WHERE id_evento = %s
            """, (id_evento_form,), uno=True)

            if not evento:
                flash('El evento seleccionado no existe.', 'error')
                return redirect(url_for('comprar'))

            if evento['precio'] is None or float(evento['precio']) < 0:
                flash('El precio del evento no es válido.', 'error')
                return redirect(url_for('comprar'))

            total = round(float(evento['precio']) * cantidad, 2)
            token_qr = uuid.uuid4().hex

            id_compra = ejecutar("""
                INSERT INTO compras
                    (id_usuario, id_evento, cantidad, total, estado, token_qr)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                session['id_usuario'],
                id_evento_form,
                cantidad,
                total,
                'Registrada',
                token_qr
            ))

            flash('Compra registrada correctamente.', 'success')
            return redirect(url_for(
                'comprobante',
                id_compra=id_compra
            ))

        except (ValueError, TypeError, Error):
            app.logger.exception('Error al registrar compra')
            flash(
                'No se pudo registrar la compra. Revisa la terminal de Flask.',
                'error'
            )

    evento = None

    if id_evento is not None:
        evento = consulta("""
            SELECT id_evento, nombre, fecha, precio
            FROM eventos
            WHERE id_evento = %s
        """, (id_evento,), uno=True)

        if not evento:
            flash('El evento seleccionado no existe.', 'error')
            return redirect(url_for('comprar'))

    return render_template(
        'comprar.html',
        eventos=eventos_disponibles,
        evento=evento,
        id_evento=id_evento
    )

# CONSULTAR LAS COMPRAS DEL USUARIO
@app.route('/mis-compras')
@requiere_login
def mis_compras():
    compras_usuario = consulta("""
        SELECT
            c.id_compra,
            c.cantidad,
            c.total,
            c.estado,
            c.fecha_compra,
            e.nombre AS nombre_evento,
            e.fecha AS fecha_evento
        FROM compras c
        INNER JOIN eventos e
            ON e.id_evento = c.id_evento
        WHERE c.id_usuario = %s
        ORDER BY c.fecha_compra DESC
    """, (session['id_usuario'],))

    return render_template(
        'mis_compras.html',
        compras=compras_usuario
    )

# COMPROBANTE DE COMPRA CON CÓDIGO QR
@app.route('/comprobante/<int:id_compra>')
@requiere_login
def comprobante(id_compra):
    compra = consulta("""
        SELECT c.id_compra, c.id_usuario, c.id_evento,
               c.cantidad, c.total, c.estado, c.fecha_compra,
               c.token_qr, e.nombre AS nombre_evento,
               e.fecha AS fecha_evento, e.hora AS hora_evento,
               u.nombre AS nombre_usuario
        FROM compras c
        JOIN eventos e ON e.id_evento = c.id_evento
        JOIN usuarios u ON u.id_usuario = c.id_usuario
        WHERE c.id_compra = %s
    """, (id_compra,), uno=True)

    if not compra:
        return 'Compra no encontrada', 404

    # Cada usuario solo puede consultar sus propias compras.
    if (
        compra['id_usuario'] != session.get('id_usuario')
        and session.get('rol') != 'admin'
    ):
        return 'No tienes permiso para ver este comprobante.', 403

    # Dirección base del sitio.
    # Para abrir el QR desde otro dispositivo, configura APP_PUBLIC_URL.
    url_publica = os.getenv('APP_PUBLIC_URL', request.url_root.rstrip('/'))
    enlace_qr = (
        url_publica.rstrip('/')
        + url_for('verificar_compra', token=compra['token_qr'])
    )

    codigo = qrcode.make(enlace_qr)
    memoria = io.BytesIO()
    codigo.save(memoria, format='PNG')

    qr_base64 = base64.b64encode(memoria.getvalue()).decode('utf-8')

    return render_template(
        'comprobante.html',
        compra=compra,
        qr_base64=qr_base64
    )


# PÁGINA PÚBLICA QUE ABRE EL QR
@app.route('/verificar-compra/<token>')
def verificar_compra(token):
    compra = consulta("""
        SELECT c.id_compra, c.cantidad, c.total, c.estado,
               c.fecha_compra, e.nombre AS nombre_evento,
               e.fecha AS fecha_evento, e.hora AS hora_evento
        FROM compras c
        JOIN eventos e ON e.id_evento = c.id_evento
        WHERE c.token_qr = %s
    """, (token,), uno=True)

    if not compra:
        return 'Código QR no válido o compra no encontrada.', 404

    return render_template(
        'verificar_compra.html',
        compra=compra
    )

# CONTACTO.
@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip().lower()
        mensaje = request.form.get('mensaje', '').strip()
        id_usuario = session.get('id_usuario')
        if not nombre or not correo or not mensaje:
            flash('Completa nombre, correo y mensaje.', 'error')
        else:
            try:
                ejecutar('''INSERT INTO mensajes_contacto (id_usuario, nombre, correo, mensaje)
                            VALUES (%s, %s, %s, %s)''', (id_usuario, nombre, correo, mensaje))
                flash('Tu mensaje fue enviado.', 'success')
                return redirect(url_for('contacto'))
            except Error:
                app.logger.exception('Error al guardar mensaje')
                flash('No se pudo enviar el mensaje.', 'error')
    return render_template('contacto.html')


# PANEL ADMINISTRADOR. Las páginas administrativas quedan protegidas por rol.

# PANEL ADMINISTRADOR

@app.route('/administrar')
@app.route('/admin')
@requiere_admin
def administrar():
    resumen = {
        'usuarios': consulta('SELECT COUNT(*) AS total FROM usuarios', uno=True)['total'],
        'lugares': consulta('SELECT COUNT(*) AS total FROM lugares', uno=True)['total'],
        'eventos': consulta('SELECT COUNT(*) AS total FROM eventos', uno=True)['total'],
        'compras': consulta('SELECT COUNT(*) AS total FROM compras', uno=True)['total'],
        'reservaciones': consulta('SELECT COUNT(*) AS total FROM reservaciones', uno=True)['total'],
        'mensajes': consulta('SELECT COUNT(*) AS total FROM mensajes_contacto', uno=True)['total']
    }

    reservaciones = consulta("""
        SELECT r.*, l.nombre AS nombre_lugar
        FROM reservaciones r
        LEFT JOIN lugares l ON l.id_lugar = r.id_lugar
        ORDER BY r.id_reserva DESC
    """)

    establecimientos = consulta("""
        SELECT
            e.id_establecimiento,
            e.id_lugar,
            e.nombre,
            e.correo,
            e.activo,
            l.nombre AS nombre_lugar
        FROM establecimientos e
        INNER JOIN lugares l ON l.id_lugar = e.id_lugar
        ORDER BY e.id_establecimiento DESC
    """)

    lugares_disponibles = consulta("""
        SELECT l.id_lugar, l.nombre, l.categoria
        FROM lugares l
        LEFT JOIN establecimientos e ON e.id_lugar = l.id_lugar
        WHERE e.id_establecimiento IS NULL
        ORDER BY l.nombre
    """)

    return render_template(
        'administrar.html',
        resumen=resumen,
        reservaciones=reservaciones,
        establecimientos=establecimientos,
        lugares_disponibles=lugares_disponibles
    )
    
# =========================================
# ADMINISTRAR CUENTAS DE ESTABLECIMIENTOS
# =========================================

@app.route('/admin/establecimientos/crear', methods=['POST'])
@requiere_admin
def admin_crear_establecimiento():
    id_lugar = request.form.get('id_lugar', type=int)
    nombre = request.form.get('nombre', '').strip()
    correo = request.form.get('correo', '').strip().lower()
    password = request.form.get('password', '')

    if not id_lugar or not nombre or not correo or not password:
        flash('Completa todos los campos.', 'error')
        return redirect(url_for('administrar') + '#establecimientos')

    if len(password) < 8:
        flash('La contraseña debe tener al menos 8 caracteres.', 'error')
        return redirect(url_for('administrar') + '#establecimientos')

    # Verificar que el lugar exista.
    lugar = consulta(
        'SELECT id_lugar FROM lugares WHERE id_lugar = %s',
        (id_lugar,),
        uno=True
    )

    if not lugar:
        flash('El lugar seleccionado no existe.', 'error')
        return redirect(url_for('administrar') + '#establecimientos')

    # Evitar que un lugar tenga dos cuentas.
    cuenta_lugar = consulta(
        'SELECT id_establecimiento FROM establecimientos WHERE id_lugar = %s',
        (id_lugar,),
        uno=True
    )

    if cuenta_lugar:
        flash('Ese lugar ya tiene una cuenta de establecimiento.', 'error')
        return redirect(url_for('administrar') + '#establecimientos')

    # Verificar que el correo no esté registrado.
    cuenta_correo = consulta(
        'SELECT id_establecimiento FROM establecimientos WHERE correo = %s',
        (correo,),
        uno=True
    )

    if cuenta_correo:
        flash('Ese correo ya está registrado como establecimiento.', 'error')
        return redirect(url_for('administrar') + '#establecimientos')

    password_hash = generate_password_hash(password)

    try:
        ejecutar("""
            INSERT INTO establecimientos
                (id_lugar, nombre, correo, password_hash, activo)
            VALUES (%s, %s, %s, %s, 1)
        """, (id_lugar, nombre, correo, password_hash))

        flash('La cuenta del establecimiento se creó correctamente.', 'success')

    except Error:
        flash('No se pudo crear la cuenta. Revisa los datos e inténtalo de nuevo.', 'error')

    return redirect(url_for('administrar') + '#establecimientos')


@app.route(
    '/admin/establecimientos/<int:id_establecimiento>/estado',
    methods=['POST']
)
@requiere_admin
def admin_estado_establecimiento(id_establecimiento):
    activo = request.form.get('activo')

    if activo not in ('0', '1'):
        flash('Estado no válido.', 'error')
        return redirect(url_for('administrar') + '#establecimientos')

    establecimiento = consulta(
        'SELECT id_establecimiento FROM establecimientos WHERE id_establecimiento = %s',
        (id_establecimiento,),
        uno=True
    )

    if not establecimiento:
        flash('No se encontró el establecimiento.', 'error')
        return redirect(url_for('administrar') + '#establecimientos')

    try:
        ejecutar(
            'UPDATE establecimientos SET activo = %s WHERE id_establecimiento = %s',
            (int(activo), id_establecimiento)
        )
        flash('Se actualizó el acceso del establecimiento.', 'success')

    except Error:
        flash('No se pudo actualizar el acceso.', 'error')

    return redirect(url_for('administrar') + '#establecimientos')

@app.route('/admin/eventos', methods=['GET', 'POST'])
@requiere_admin
def admin_eventos():
    if request.method == 'POST':
        try:
            ejecutar(
                '''INSERT INTO eventos
                (id_lugar, nombre, descripcion, fecha, hora, lugar, precio)
                VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                (
                    request.form['id_lugar'],
                    request.form['nombre'],
                    request.form.get('descripcion') or None,
                    request.form.get('fecha') or None,
                    request.form.get('hora') or None,
                    request.form.get('lugar') or None,
                    request.form.get('precio') or 0
                )
            )
            flash('Evento agregado correctamente.', 'success')
            return redirect(url_for('admin_eventos'))

        except (Error, KeyError, ValueError):
            app.logger.exception('Error al agregar evento')
            flash('No se pudo agregar el evento.', 'error')

    lista = consulta('''
        SELECT e.*, l.nombre AS nombre_lugar
        FROM eventos e
        LEFT JOIN lugares l ON l.id_lugar = e.id_lugar
        ORDER BY e.fecha DESC
    ''')

    lugares = consulta(
        'SELECT id_lugar, nombre FROM lugares ORDER BY nombre'
    )

    return render_template(
        'admin_eventos.html',
        eventos=lista,
        lugares=lugares
    )


@app.route('/admin/eventos/eliminar/<int:id_evento>', methods=['POST'])
@requiere_admin
def admin_eliminar_evento(id_evento):
    try:
        ejecutar(
            'DELETE FROM eventos WHERE id_evento = %s',
            (id_evento,)
        )
        flash('Evento eliminado correctamente.', 'success')
    except Error:
        app.logger.exception('Error al eliminar evento')
        flash('No se pudo eliminar el evento.', 'error')

    return redirect(url_for('admin_eventos'))

@app.route('/admin/compras')
@requiere_admin
def admin_compras():
    lista = consulta('''SELECT c.*, u.nombre AS nombre_usuario,
                           e.nombre AS nombre_evento
                    FROM compras c
                    JOIN usuarios u ON u.id_usuario = c.id_usuario
                    JOIN eventos e ON e.id_evento = c.id_evento
                    ORDER BY c.fecha_compra DESC''')
    return render_template('admin_compras.html', compras=lista)


@app.route('/admin/reservaciones')
@requiere_admin
def admin_reservaciones():
    lista = consulta('''SELECT r.*, l.nombre AS nombre_lugar FROM reservaciones r
                        JOIN lugares l ON l.id_lugar=r.id_lugar ORDER BY r.fecha DESC''')
    return render_template('admin_reservaciones.html', reservaciones=lista)


@app.route('/admin/reservaciones/estado/<int:id_reserva>', methods=['POST'])
@requiere_admin
def admin_estado_reservacion(id_reserva):
    estado = request.form.get('estado')

    if estado not in ('Pendiente', 'Confirmada', 'Cancelada'):
        flash('Estado inválido.', 'error')
    else:
        try:
            ejecutar(
                'UPDATE reservaciones SET estado = %s WHERE id_reserva = %s',
                (estado, id_reserva)
            )
            flash('Estado de reservación actualizado.', 'success')
        except Error:
            app.logger.exception('Error al actualizar la reservación')
            flash('No se pudo actualizar el estado.', 'error')

    return redirect(url_for('administrar') + '#reservaciones')

@app.route('/admin/usuarios')
@requiere_admin
def admin_usuarios():
    lista = consulta('''SELECT id_usuario, nombre, correo, telefono, rol, creado_en
                        FROM usuarios ORDER BY creado_en DESC''')
    return render_template('admin_usuarios.html', usuarios=lista)


@app.route('/admin/mensajes')
@requiere_admin
def admin_mensajes():
    lista = consulta('SELECT * FROM mensajes_contacto ORDER BY fecha_envio DESC')
    return render_template('admin_mensajes.html', mensajes=lista)


@app.route('/admin/mensajes/estado/<int:id_mensaje>', methods=['POST'])
@requiere_admin
def admin_estado_mensaje(id_mensaje):
    estado = request.form.get('estado')
    if estado not in ('Pendiente', 'Atendido'):
        flash('Estado inválido.', 'error')
    else:
        ejecutar('UPDATE mensajes_contacto SET estado=%s WHERE id_mensaje=%s', (estado, id_mensaje))
        flash('Estado del mensaje actualizado.', 'success')
    return redirect(url_for('admin_mensajes'))



# =========================================
# INICIO DE SESION DE ESTABLECIMIENTOS
# =========================================

@app.route('/login-establecimiento', methods=['GET', 'POST'])
def login_establecimiento():
    if request.method == 'POST':
        correo = request.form.get('correo', '').strip().lower()
        password = request.form.get('password', '')

        establecimiento = consulta("""
            SELECT id_establecimiento, id_lugar, nombre,
                   correo, password_hash, activo
            FROM establecimientos
            WHERE correo = %s
            LIMIT 1
        """, (correo,), uno=True)

        if not establecimiento or not check_password_hash(
            establecimiento['password_hash'], password
        ):
            flash('Correo o contraseña incorrectos.', 'error')
            return redirect(url_for('login_establecimiento'))

        if not establecimiento['activo']:
            flash('Esta cuenta está desactivada. Contacta al administrador.', 'error')
            return redirect(url_for('login_establecimiento'))

        # Crear una sesión exclusiva para el establecimiento.
        session.clear()
        session['id_establecimiento'] = establecimiento['id_establecimiento']
        session['id_lugar_establecimiento'] = establecimiento['id_lugar']
        session['nombre_establecimiento'] = establecimiento['nombre']

        return redirect(url_for('panel_establecimiento'))

    return render_template('login_establecimiento.html')


# =========================================
# PANEL DEL ESTABLECIMIENTO
# =========================================

@app.route('/establecimiento/panel')
def panel_establecimiento():
    if not session.get('id_establecimiento'):
        flash('Inicia sesión con tu cuenta de establecimiento.', 'error')
        return redirect(url_for('login_establecimiento'))

    establecimiento = consulta("""
        SELECT e.nombre, e.correo, e.activo, l.nombre AS nombre_lugar
        FROM establecimientos e
        INNER JOIN lugares l ON l.id_lugar = e.id_lugar
        WHERE e.id_establecimiento = %s
        LIMIT 1
    """, (session['id_establecimiento'],), uno=True)

    if not establecimiento or not establecimiento['activo']:
        session.clear()
        flash('La cuenta no está disponible. Contacta al administrador.', 'error')
        return redirect(url_for('login_establecimiento'))

    return render_template(
        'panel_establecimiento.html',
        establecimiento=establecimiento
    )


# =========================================
# CERRAR SESION DEL ESTABLECIMIENTO
# =========================================

@app.route('/establecimiento/cerrar-sesion')
def logout_establecimiento():
    session.pop('id_establecimiento', None)
    session.pop('id_lugar_establecimiento', None)
    session.pop('nombre_establecimiento', None)

    flash('Sesión de establecimiento cerrada.', 'success')
    return redirect(url_for('login_establecimiento'))


@app.errorhandler(404)
def no_encontrado(error):
    return 'Página no encontrada. Revisa la dirección o el nombre de la plantilla.', 404


@app.errorhandler(500)
def error_servidor(error):
    app.logger.exception('Error interno de la aplicación')
    return 'Ocurrió un error en la aplicación. Revisa la terminal de Flask para ver el detalle.', 500

def probar_conexion():
    try:
        conexion = conectar_db()
        print("CONEXIÓN A MYSQL CORRECTA")
        print("Base de datos:", conexion.database)
        conexion.close()
    except Error as e:
        print("ERROR DE CONEXIÓN A MYSQL:")
        print(e)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
