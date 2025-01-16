from flask import Flask, render_template, flash, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy  # Base de datos
from flask_migrate import Migrate  # Versiones de bases de datos
from flask_login import LoginManager, logout_user, current_user, login_required, login_user
import datetime
import  os 
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import jsonify
from dotenv import load_dotenv
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys
from transbank.common.integration_type import IntegrationType
import logging, uuid


UPLOAD_FOLDER = 'static/imagenes'  
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

COMMERCE_CODE = "597055555532"  
API_KEY = "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C"  

if not COMMERCE_CODE or not API_KEY:
    raise ValueError("Las credenciales de Webpay no están configuradas correctamente.")

BASE_URL = "http://localhost:5000"  # Cambiar según tu dominio/localhost
Transaction.commerce_code = COMMERCE_CODE
Transaction.api_key = API_KEY
Transaction.environment = "TEST"

# Configurar el nivel de logs
logging.basicConfig(level=logging.DEBUG)

app.logger.setLevel(logging.DEBUG)

app.config["SECRET_KEY"] = "losrockstars"  
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root@localhost/rockstars"  
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'imagenes') 
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

# Inicialización de LoginManager
login_manager = LoginManager(app)
login_manager.login_view = "login_admin" 

Migrate(app, db)

# Importar los formularios y modelos
from forms import FormularioRegistro, FormularioLoginAdministrador, FormularioRegistroAdministrador
from controlers import ControladorAdministrador
from models import Usuario, Administrador, Pieza, Reserva, Pago

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def principal():
    piezas = Pieza.query.all()
    return render_template("base_template.html", piezas = piezas)



@login_manager.user_loader
def load_user(user_id):
    return Administrador.query.get(int(user_id))

#Ingreso de Administradores
@app.route('/AdministradoresLosRockstarslogin', methods=['GET', 'POST'])
def login_admin():
    form_acceso = FormularioLoginAdministrador()

    if form_acceso.validate_on_submit():
        correo = form_acceso.correo.data
        contraseña = form_acceso.contraseña.data

        admin = Administrador.obtener_por_correo(correo)

        if admin:
            if admin.chequeo_clave(contraseña):
                login_user(admin)  
                flash("Inicio de sesión exitoso", category="success")
                return redirect("/") 
            else:
                flash("Contraseña incorrecta", category="danger")
        else:
            flash("Usuario no encontrado", category="danger")


    return render_template("sesion_admin.html", form_acceso=form_acceso)



#Registro de administradores funcional. Guarda en la base de datos
@app.route('/AdministradoresLosRockstarsregistro', methods=['GET', 'POST'])
def registro_admin():
    if not current_user.is_anonymous:
        return redirect("/") 

    form = FormularioRegistroAdministrador()
    
    if form.validate_on_submit():
        correo = form.correo.data
        contraseña = form.contraseña.data
        confirmar_contraseña = form.confirmar_contraseña.data

        # Verificar si las contraseñas coinciden
        if contraseña != confirmar_contraseña:
            flash("Las contraseñas no coinciden", "danger")
            return render_template("registrarse_admin.html", form_registro=form)

        # Verificar si el correo ya está registrado
        admin = Administrador().obtener_por_correo(correo)
        if admin is not None:
            flash(f"El correo {correo} ya se encuentra registrado.", "danger")
            return render_template("registrarse_admin.html", form_registro=form)

        # Crear el usuario
        ControladorAdministrador().crear_usuario(correo, contraseña)
        flash(f"Registro exitoso para el usuario {correo}", "success")
        return redirect("/AdministradoresLosRockstarslogin")


    return render_template('registrarse_admin.html', form_registro=form)

#Cerrar sesion
@app.route('/logout', methods=['GET', 'POST'])
@login_required  
def logout_admin():
    if current_user.es_admin(): 
        logout_user()  
        flash("Has cerrado sesión exitosamente.", category="success")
        return redirect("/") 
    else:
        flash("Acción no permitida. No eres un administrador.", category="danger")
        return redirect("/")

@app.route("/registro/<int:habitacion_id>", methods=['GET', 'POST'])
def register(habitacion_id):

    habitacion = Pieza.query.get(habitacion_id)
    if not habitacion:
        flash("Habitación no encontrada.", "danger")
        return redirect(url_for('vista_piezas'))  
    
    longitud_numero_celular = 0  

    if request.method == "POST":
        nombre_apellido = request.form['nombre_apellido']
        rut_pasaporte = request.form.get('rut') or request.form.get('pasaporte')
        fecha_nacimiento = request.form['fecha_nacimiento']
        pais = request.form['pais']
        numero_celular = str(request.form['numero_celular'])
        correo = request.form["correo"]
        personas = request.form.get('personas')

        longitudes_pais = {
            'AR': 12, 
            'BR': 13, 
            'CA': 12,  
            'CL': 12,  
            'CO': 12,
            'MX': 13,  
            'PE': 13,  
            'US': 12, 
            'UY': 12,  
            'VE': 13,  
            'FR': 13, 
            'DE': 13, 
            'IT': 13,  
            'NL': 13,  
            'PT': 13, 
            'ES': 13, 
            'SE': 13, 
            'CH': 13, 
            'GB': 13,  
            'AU': 13, 
            'IN': 14,  
            'CN': 14,  
            'JP': 14, 
            'KR': 14,  
            'RU': 14, 
            'ZA': 13,  
        }

        longitud_numero_celular = longitudes_pais.get(pais, 0)

        if not personas or not personas.strip().isdigit():
            flash("La cantidad de personas debe ser un número válido mayor a 0.", "danger")
            return redirect(url_for('register', habitacion_id=habitacion_id))
        personas = int(personas)
        if personas > habitacion.cantidad_personas:
            flash(f"La habitación solo tiene capacidad para {habitacion.cantidad_personas} personas.", "danger")
            return redirect(url_for('register', habitacion_id=habitacion_id))
        
        llegada = request.form.get('llegada')
        salida = request.form.get('salida')

        overlapping_reservas = Reserva.query.filter(
            Reserva.habitacion_id == habitacion_id,
            db.or_(db.and_(Reserva.fecha_llegada <= salida,Reserva.fecha_salida >= llegada))).all()
        if overlapping_reservas:
            flash("La habitación ya está reservada para las fechas seleccionadas.", "danger")
            return redirect(url_for('register', habitacion_id=habitacion_id))
        
        nuevo_usuario = Usuario(
            nombre_apellido=nombre_apellido,
            rut_pasaporte=rut_pasaporte,
            fecha_nacimiento=fecha_nacimiento,
            pais=pais,
            numero_celular=numero_celular,
            correo=correo,
            fecha_llegada=llegada,
            fecha_salida=salida,
            cantidad_personas=personas,
            habitacion_id=habitacion_id
        )
        db.session.add(nuevo_usuario)
        db.session.commit()

        nueva_reserva = Reserva(
            habitacion_id=habitacion_id,
            fecha_llegada=llegada,
            fecha_salida=salida,
            cantidad_personas=personas,
            usuario_id=nuevo_usuario.id
        )
        db.session.add(nueva_reserva)
        db.session.commit()

        flash("Usuario y reserva registrados con éxito.", "success")
        return redirect(url_for('iniciar_pago'))
    
    llegada = request.args.get('llegada')
    salida = request.args.get('salida')
    cantidad_personas = request.args.get('personas')

    return render_template('registro.html', 
                           llegada=llegada, 
                           salida=salida, 
                           cantidad_personas=cantidad_personas, 
                           pieza_id=habitacion_id, 
                           capacidad_habitacion=habitacion.cantidad_personas,
                           longitud_numero_celular=longitud_numero_celular)

@app.route('/agregarpieza', methods=['GET', 'POST'])
def agregar_pieza():
    if request.method == 'POST':
        nombre_pieza = request.form['nombre_pieza']
        descripcion_pieza = request.form['descripcion_pieza']
        cantidad_personas = int(request.form['cantidad_personas'])
        precio_pieza = float(request.form['precio_pieza'])

        # Subir las imágenes
        imagenes = []
        if 'imagenes_pieza' not in request.files:
            flash("No se seleccionaron archivos.", "danger")
            return redirect(request.url)

        files = request.files.getlist('imagenes_pieza')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                imagenes.append(filename)

        nueva_pieza = Pieza(
            nombre_pieza=nombre_pieza,
            descripcion_pieza=descripcion_pieza,
            cantidad_personas=cantidad_personas,
            precio_pieza=precio_pieza,
            imagen_pieza=",".join(imagenes)  
        )

        db.session.add(nueva_pieza)
        db.session.commit()

        flash("Habitación agregada con éxito.", "success")
        return redirect(url_for('vista_piezas')) 
    return render_template('agregar_piezas.html') 


@app.route('/modificarpieza/<int:id_pieza>', methods=['GET', 'POST'])
def modificar_pieza(id_pieza):
    pieza = Pieza.query.get_or_404(id_pieza)

    if request.method == 'POST':
        if 'eliminar' in request.form:
            db.session.delete(pieza)
            db.session.commit()
            flash("Habitación eliminada con éxito.", "success")
            return redirect(url_for('principal'))

        pieza.nombre_pieza = request.form['nombre_pieza']
        pieza.descripcion_pieza = request.form['descripcion_pieza']
        pieza.cantidad_personas = int(request.form['cantidad_personas'])
        pieza.precio_pieza = float(request.form['precio_pieza'])
        pieza.descuento = float(request.form['descuento'])

        imagenes = pieza.imagen_pieza.split(",") if pieza.imagen_pieza else []
        if 'imagenes_pieza' in request.files:
            files = request.files.getlist('imagenes_pieza')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    imagenes.append(filename)

        pieza.imagen_pieza = ",".join(imagenes)
        db.session.commit()

        flash("Pieza modificada con éxito.", "success")
        return redirect(url_for('principal'))

    return render_template('modificar_piezas.html', pieza=pieza)


@app.route('/vista_piezas', methods=['POST'])
def vista_piezas():
    llegada = request.form.get('llegada')
    salida = request.form.get('salida')
    personas = request.form.get('personas', type=int)

    if llegada and salida:
        if len(llegada) == 10 and len(salida) == 10:
            if llegada[4] == '-' and llegada[7] == '-' and salida[4] == '-' and salida[7] == '-':
                if not (llegada[:4].isdigit() and llegada[5:7].isdigit() and llegada[8:10].isdigit()):
                    flash("La fecha de llegada no tiene un formato válido.", "danger")
                    return redirect(url_for('vista_piezas'))

                if not (salida[:4].isdigit() and salida[5:7].isdigit() and salida[8:10].isdigit()):
                    flash("La fecha de salida no tiene un formato válido.", "danger")
                    return redirect(url_for('vista_piezas'))

                llegada = datetime.strptime(llegada, '%Y-%m-%d')
                salida = datetime.strptime(salida, '%Y-%m-%d')

                if salida <= llegada:
                    flash("La fecha de salida debe ser posterior a la fecha de llegada.", "danger")
                    return redirect(url_for('vista_piezas'))

                piezas_disponibles = Pieza.query.filter(Pieza.cantidad_personas >= personas).filter(
                    ~Pieza.reservas.any(db.and_(
                        Reserva.fecha_llegada < salida,
                        Reserva.fecha_salida > llegada
                    ))
                ).all()

                dias_estancia = (salida - llegada).days
                if dias_estancia <= 0:
                    flash("La estancia debe ser de al menos un día.", "danger")
                    return redirect(url_for('vista_piezas'))

                for pieza in piezas_disponibles:
                    pieza.precio_total = (pieza.precio_pieza - (pieza.precio_pieza * pieza.descuento / 100)) * dias_estancia

            else:
                flash("El formato de las fechas debe ser YYYY-MM-DD.", "danger")
                return redirect(url_for('vista_piezas'))
        else:
            flash("Las fechas deben estar en formato YYYY-MM-DD.", "danger")
            return redirect(url_for('vista_piezas'))
    else:
        piezas_disponibles = Pieza.query.all()
        dias_estancia = 0  

        for pieza in piezas_disponibles:
            pieza.precio_total = pieza.precio_pieza - (pieza.precio_pieza * pieza.descuento / 100)

    return render_template(
        "piezas_disponibles.html", 
        piezas=piezas_disponibles, 
        llegada=llegada, 
        salida=salida, 
        personas=personas, 
        dias_estancia=dias_estancia
    )

@app.route('/estadisticas', methods=['GET'])
def estadisticas():
    resultados = (db.session.query(Usuario.pais, db.func.sum(Usuario.cantidad_personas)).group_by(Usuario.pais).all())
    estadisticas = {pais: cantidad for pais, cantidad in resultados}

    habitacion_mas_reservada = (db.session.query(Pieza.nombre_pieza, Pieza.imagen_pieza, db.func.count(Reserva.id)).join(Reserva, Pieza.id == Reserva.habitacion_id).group_by(Pieza.id).order_by(db.func.count(Reserva.id).desc()).first()  )

    return render_template(
        'estadisticas.html',
        estadisticas=estadisticas,
        habitacion_mas_reservada=habitacion_mas_reservada
    )
@app.route('/api/datos_grafico', methods=['GET'])
def api_datos_grafico():
    resultados = (
        db.session.query(
            Pieza.nombre_pieza,
            db.func.year(Reserva.fecha_llegada).label('año'),
            db.func.month(Reserva.fecha_llegada).label('mes'),
            db.func.sum((Pieza.precio_pieza - (Pieza.precio_pieza * Pieza.descuento / 100)) * db.func.datediff(Reserva.fecha_salida, Reserva.fecha_llegada)).label('ganancia')
        )
        .join(Reserva, Pieza.id == Reserva.habitacion_id)
        .group_by(Pieza.nombre_pieza, 'año', 'mes')
        .order_by('año', 'mes')
        .all()
    )

    # Formatear datos en un diccionario
    datos_grafico = {}
    for nombre, año, mes, ganancia in resultados:
        ganancia = ganancia or 0  # 
        clave = f"{año}-{mes:02d}"
        if clave not in datos_grafico:
            datos_grafico[clave] = {}
        datos_grafico[clave][nombre] = ganancia

    return jsonify(datos_grafico)

@app.route('/estadisticas_ganancias', methods=['GET'])
def estadisticas_ganancias():
    resultados = (
        db.session.query(
            Pieza.nombre_pieza,
            db.func.year(Reserva.fecha_llegada).label('año'),
            db.func.month(Reserva.fecha_llegada).label('mes'),
            db.func.sum((Pieza.precio_pieza - (Pieza.precio_pieza * Pieza.descuento / 100)) * db.func.datediff(Reserva.fecha_salida, Reserva.fecha_llegada)).label('ganancia')
        )
        .join(Reserva, Pieza.id == Reserva.habitacion_id)
        .group_by(Pieza.nombre_pieza, 'año', 'mes')
        .order_by('año', 'mes')
        .all()
    )

    datos_grafico = {}
    for nombre, año, mes, ganancia in resultados:
        ganancia = ganancia or 0  
        clave = f"{año}-{mes:02d}"
        if clave not in datos_grafico:
            datos_grafico[clave] = {}
        datos_grafico[clave][nombre] = ganancia

    return render_template('estadisticas_ganancias.html', datos_grafico=datos_grafico)


@app.route('/quienessomos')
def quienes_somos():
    return render_template('quienessomos.html')

@app.route('/economia-circular')
def economia_circular():
    return render_template('economia_circular.html')

@app.route('/convenios-alianzas')
def convenios_alianzas():
    return render_template('convenios_alianzas.html')

@app.route('/panoramas')
def panoramas():
    return render_template('panoramas.html')

import uuid

def obtener_datos_pago():

    buy_order = str(uuid.uuid4())[:26]  
    session_id = str(uuid.uuid4())
    amount = 12000  
    return buy_order, session_id, amount


@app.route("/iniciar_pago")
def iniciar_pago():
    buy_order, session_id, amount = obtener_datos_pago()
    return_url = f"{BASE_URL}/resultado_pago"

    try:
        tx = Transaction()
        response = tx.create(buy_order, session_id, amount, return_url)

        url = response["url"]
        token = response["token"]

        return render_template("pago.html", url=url, token=token)
    except Exception as e:
        return render_template("error.html", error_message="Error al iniciar el pago: " + str(e))
@app.route("/resultado_pago", methods=["GET", "POST"])
def resultado_pago():
    token_ws = request.args.get('token_ws')

    if not token_ws:
        return render_template("error.html", error_message="No se ha recibido el token del pago.")

    try:
        tx = Transaction()

        response = tx.commit(token_ws)

        print(f"Respuesta del sistema de pago: {response}")

        status = response.get("status")
        buy_order = response.get("buy_order")
        amount = response.get("amount")

        if not status:
            return render_template("error.html", error_message="No se ha recibido el estado del pago.")
        
        if status == 'ABORTED':
            error_message = response.get('error_message', 'La transacción fue abortada.')
            return render_template("error.html", error_message=f"Error en el pago: {error_message}")
        
        nuevo_pago = Pago(
            orden_compra=buy_order,
            monto=amount,
            estado=status,
            token_ws=token_ws
        )
        db.session.add(nuevo_pago)
        db.session.commit()

        return redirect(url_for("exito_pago", status=status, buy_order=buy_order, amount=amount))

    except Exception as e:
        return render_template("error.html", error_message="Error al procesar el pago: " + str(e))

@app.route("/exito_pago")
def exito_pago():
    buy_order = request.args.get("buy_order")
    amount = request.args.get("amount")
    status = request.args.get("status")

    if not buy_order or not amount or not status:
        return render_template("error.html", error_message="Faltan parámetros en la respuesta del pago.")

    if status == "AUTHORIZED":
        return render_template("exito_pago.html", buy_order=buy_order, amount=amount, status=status)
    else:
        return render_template("error.html", error_message="Pago no autorizado o fallido.")

@app.route('/fallo_pago')
def fallo_pago():
    return "<h1>Hubo un problema con el pago.</h1><p>Por favor, intenta nuevamente.</p>"

@app.route('/error_pago')
def error_pago():
    error_message = request.args.get('error_message', 'Ocurrió un error desconocido')
    return f"<h1>Error al procesar el pago</h1><p>{error_message}</p>"