from flask import Flask, render_template, flash, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy  # Base de datos
from flask_migrate import Migrate  # Versiones de bases de datos
from flask_login import LoginManager, logout_user, current_user, login_required, login_user
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import jsonify
import re, os

UPLOAD_FOLDER = 'static/imagenes'  
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
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
from models import Usuario, Administrador, Pieza, Reserva

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

    if request.method == "POST":
        nombre_apellido = request.form['nombre_apellido']
        rut_pasaporte = request.form.get('rut') or request.form.get('pasaporte')
        fecha_nacimiento = request.form['fecha_nacimiento']
        pais = request.form['pais']
        numero_celular = request.form['numero_celular']
        correo = request.form["correo"]
        personas = request.form.get('personas')

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
            habitacion_id = habitacion_id
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
        return redirect(url_for('principal'))
    llegada = request.args.get('llegada')
    salida = request.args.get('salida')
    cantidad_personas = request.args.get('personas')

    return render_template('registro.html', llegada=llegada, salida=salida, cantidad_personas=cantidad_personas, pieza_id=habitacion_id, capacidad_habitacion=habitacion.cantidad_personas)

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
        pieza.nombre_pieza = request.form['nombre_pieza']
        pieza.descripcion_pieza = request.form['descripcion_pieza']
        pieza.cantidad_personas = int(request.form['cantidad_personas'])
        pieza.precio_pieza = float(request.form['precio_pieza'])

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


@app.route("/vista_piezas", methods=['POST'])
def vista_piezas():

    llegada = request.form.get('llegada')
    salida = request.form.get('salida')
    personas = request.form.get('personas', type=int)

    if llegada and salida:
        llegada = datetime.strptime(llegada, '%Y-%m-%d')
        salida = datetime.strptime(salida, '%Y-%m-%d')
        piezas_disponibles = Pieza.query.filter(
            Pieza.cantidad_personas >= personas
        ).filter(~Pieza.reservas.any(db.and_(Reserva.fecha_llegada < salida,Reserva.fecha_salida > llegada))).all()
    else:
        piezas_disponibles = Pieza.query.all()
    return render_template("piezas_disponibles.html", piezas=piezas_disponibles, llegada=llegada, salida=salida, personas=personas)


