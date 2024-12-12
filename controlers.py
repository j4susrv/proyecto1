from models import Administrador
from forms import FormularioRegistroLoginAdministrador  
from app import db
from werkzeug.security import generate_password_hash
#Controlador de los Administradores
#maneja en parte el correo, la contraseña y el confirmar conrtaseña creando el usuario si las contraseñas son las mismas
class ControladorAdministrador():
    def crear_usuario(self, correo, contraseña, confirmar_contraseña):
        if contraseña != confirmar_contraseña:
            return "Las contraseñas no coinciden"

        # Hashea la contraseña antes de guardarla en la base de datos
        hashed_password = generate_password_hash(contraseña)

        nuevo_admin = Administrador(correo=correo, contraseña=hashed_password)
        db.session.add(nuevo_admin)
        db.session.commit()

        return "Usuario creado exitosamente"