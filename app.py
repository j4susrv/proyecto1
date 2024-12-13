from flask import Flask, render_template, flash, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy  # Base de datos
from flask_migrate import Migrate  # Versiones de bases de datos
from flask_login import LoginManager, logout_user, current_user, login_required, login_user
from datetime import datetime
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

@app.route("/vista_piezas")
def vista_piezas():
    piezas = Pieza.query.all()
    return render_template("piezas_disponibles.html", piezas = piezas)

@app.route('/registro', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre_apellido = request.form['nombre_apellido']
        rut_pasaporte = request.form['rut_pasaporte']
        fecha_nacimiento = request.form['fecha_nacimiento']
        pais = request.form['pais']
        numero_celular = request.form['numero_celular']
        correo = request.form["correo"]


        # Convertir la fecha de nacimiento a formato datetime
        fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')

        nuevo_usuario = Usuario(
            nombre_apellido=nombre_apellido,
            rut_pasaporte=rut_pasaporte,
            fecha_nacimiento=fecha_nacimiento,
            pais=pais,
            numero_celular=numero_celular,
            correo=correo
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        flash("Usuario registrado con éxito.", "success")
        return redirect(url_for('principal')) 

    return render_template('registro.html')

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

        # Crear la nueva pieza
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


@app.route('/reservar', methods=['POST'])
def reservar():
    data = request.json
    pieza_id = data.get('pieza_id')
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    usuario_id = current_user.id  

    if not pieza_id or not fecha_inicio or not fecha_fin:
        return jsonify({'error': 'Faltan datos para procesar la reserva.'}), 400

    # Convertir las fechas a formato datetime
    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')

    
    nueva_reserva = Reserva(
        pieza_id=pieza_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        usuario_id=usuario_id
    )

    db.session.add(nueva_reserva)
    db.session.commit()

    return jsonify({'mensaje': 'Reserva realizada con éxito.'})
