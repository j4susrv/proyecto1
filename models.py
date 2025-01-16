from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash  # seguridad
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import date

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre_apellido = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    rut_pasaporte = db.Column(db.String(50), nullable=True) 
    pais = db.Column(db.String(2), nullable=False) 
    numero_celular = db.Column(db.String(20), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    fecha_llegada = db.Column(db.Date, nullable = False)
    fecha_salida = db.Column(db.Date, nullable = False)
    cantidad_personas = db.Column(db.Integer, nullable = False)
    habitacion_id = db.Column(db.Integer, db.ForeignKey('habitaciones.id'), nullable=False)

    reservas = db.relationship('Reserva', back_populates='usuario', lazy=True)
    metodos_pago = db.relationship('MetodoPago', back_populates='usuario', lazy=True)

    def es_admin(self):
        return False

    @staticmethod
    def obtener_por_correo(correo):
        usuario = Usuario.query.filter_by(correo=correo).first()
        print(f"Consultando por el usuario {usuario} en db")
        return usuario

    @staticmethod
    def obtener_por_id(id):
        print(f"Consultando por el usuario con id{id} en db")
        return Usuario.query.get(id)


class Administrador(UserMixin, db.Model):
    __tablename__ = "administradores"
    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(50), nullable=False, unique=True)
    contraseña = db.Column(db.String(255), nullable=False)

    def establecer_clave(self, contraseña):
        self.contraseña = generate_password_hash(contraseña)

    def chequeo_clave(self, contraseña):
        return check_password_hash(self.contraseña, contraseña)

    def es_admin(self):
        return True

    @staticmethod
    def obtener_por_correo(correo):
        return Administrador.query.filter_by(correo=correo).first()


class Pieza(db.Model):
    __tablename__ = "habitaciones"
    id = db.Column(db.Integer, primary_key=True)
    nombre_pieza = db.Column(db.String(100), nullable=False)
    imagen_pieza = db.Column(db.String(200), nullable=True)
    descripcion_pieza = db.Column(db.Text, nullable=False)
    cantidad_personas = db.Column(db.Integer, nullable=False)
    precio_pieza = db.Column(db.Integer, nullable=False)
    descuento = db.Column(db.Float, default = 0)
    reservas = db.relationship('Reserva', back_populates='habitacion', lazy=True)


class Reserva(db.Model):
    __tablename__ = 'reservas'
    id = db.Column(db.Integer, primary_key=True)
    habitacion_id = db.Column(db.Integer, db.ForeignKey('habitaciones.id'), nullable=False)
    fecha_llegada = db.Column(db.Date, nullable=False)
    fecha_salida = db.Column(db.Date, nullable=False)
    cantidad_personas = db.Column(db.Integer, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    habitacion = db.relationship('Pieza', back_populates='reservas', lazy=True)
    usuario = db.relationship('Usuario', back_populates='reservas', lazy=True)


class MetodoPago(db.Model):
    __tablename__ = 'metodos_pago'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)  
    detalles = db.Column(db.Text, nullable=True)         
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    usuario = db.relationship('Usuario', back_populates='metodos_pago', lazy=True)

class Pago(db.Model):
    __tablename__ = 'pago'
    id = db.Column(db.Integer, primary_key=True)
    orden_compra = db.Column(db.String(50), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    token_ws = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp())