from app import db
from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash #seguridad
from sqlalchemy import Column, Integer, ForeignKey, DateTime,Date
from sqlalchemy.orm import relationship
from datetime import date


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nombre_apellido = db.Column(db.String(50), nullable=False)
    correo = db.Column(db.String(50), unique=True, nullable=False)  
    rut_pasaporte = db.Column(db.String(30), nullable=False)  
    pais = db.Column(db.String(50), nullable=False)
    numero_celular = db.Column(db.Integer, nullable= False)
    fecha_nacimiento = db.Column(db.Date, nullable = False)


    reservas = db.relationship("Reserva", back_populates="usuario")
    def es_admin(self):
        return False
    @staticmethod 
    def obtener_por_correo(correo):
        usuario = Usuario.query.filter_by(correo=correo).first()
        print(f"Consultando por el usuario {usuario} en db")
        return(usuario)
    @staticmethod
    def obtener_por_id(id):
        print(f"Consultando por el usuario con id{id} en db")
        return Usuario.query.get(id)
 
class Reserva(db.Model):
    __tablename__ = 'reservas'

    id = db.Column(db.Integer, primary_key=True)
    fecha_entrada = db.Column(db.Date, nullable=False)
    fecha_salida = db.Column(db.Date, nullable=False)
    
    usuario_id = db.Column(db.Integer, ForeignKey('usuarios.id'), nullable=False) 
    habitacion_id = db.Column(db.Integer, ForeignKey('habitaciones.id'), nullable=False)  

    usuario = relationship("Usuario", back_populates="reservas")
    habitacion = relationship("Habitacion", back_populates="reservas")

class Habitacion(db.Model):
    __tablename__ = 'habitaciones'

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(10), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)

    reservas = db.relationship("Reserva", back_populates="habitacion")


class Administrador(UserMixin,db.Model):
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