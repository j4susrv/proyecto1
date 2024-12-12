from flask import Flask, render_template, flash, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy  # Base de datos
from flask_migrate import Migrate  # Versiones de bases de datos
from flask_login import LoginManager, logout_user, current_user, login_required, login_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.config["SECRET_KEY"] = "losrockstars"  # Clave secreta para la sesión
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root@localhost/rockstars"  # URI de la base de datos
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Deshabilitar el seguimiento de modificaciones
db = SQLAlchemy(app)

# Inicialización de LoginManager
login_manager = LoginManager(app)
login_manager.login_view = "login_admin"  # Página de login cuando el usuario no está autenticado

Migrate(app, db)

# Importar los formularios y modelos
from forms import FormularioRegistro, FormularioRegistroLoginAdministrador
from controlers import ControladorAdministrador
from models import Usuario, Administrador


@app.route("/")
def principal():
    return render_template("base_template.html")


# Configurar el cargador de usuario para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Administrador.query.get(int(user_id))


@app.route('/AdministradoresLosRockstarslogin', methods=['GET', 'POST'])
def login_admin():
    form_acceso = FormularioRegistroLoginAdministrador()
    if form_acceso.validate_on_submit():
        correo = form_acceso.correo.data
        contraseña = form_acceso.contraseña.data

        admin = Administrador.obtener_por_correo(form_acceso.correo.data, correo)
        if admin:
            if admin.chequeo_clave(contraseña):
                return redirect("/")
            else:
                print("Contraseña incorrecta")
                return redirect("/")
        else:
            print("Usuario no encontrado")
            return redirect("/")
    return render_template("sesion_admin.html", form_acceso=form_acceso)

@app.route('/AdministradoresLosRockstarsregistro', methods=['GET', 'POST'])
def registro_admin():
    if not current_user.is_anonymous:
        return render_template("index.html")
    form = FormularioRegistroLoginAdministrador()  # Inicializa el formulario
    if request.method == 'POST':  # Si el método es POST, validamos el formulario
        if form.validate_on_submit():
            print("Formulario válido")
            flash("Formulario válido")
            
            correo = form.correo.data 
            contraseña = form.contraseña.data 
            confirmar_contraseña=form.confirmar_contraseña.data
            
            admin = Administrador().obtener_por_correo(correo)
            
            if admin is not None:
                error = f"El correo {correo} ya se encuentra registrado"
                print(error)
                flash(error)
                return render_template("registrarse_admin.html ", form_registro = form)

            ControladorAdministrador().crear_usuario( correo, contraseña,confirmar_contraseña)
            flash(f'Registro exitoso para el usuario {correo}')
            return redirect("/AdministradoresLosRockstarslogin")
        else:
            print("Formulario inválido")
            flash("Formulario inválido")

    # Cuando accedemos a /register con GET o si hay un error de validación
    return render_template('registrarse_admin.html', form_registro = form)



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

        # Creando un nuevo registro de usuario
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
        return redirect(url_for('register'))  # Redirigir al formulario de registro

    return render_template('registro.html')