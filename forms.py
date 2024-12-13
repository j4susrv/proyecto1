from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, TextAreaField, IntegerField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, InputRequired
class FormularioRegistro(FlaskForm):    
    nombre_apellido     = StringField('nombre_apellido', validators=[DataRequired(), Length(min=3, max=50)])
    rut_pasaporte       = StringField('rut',validators=[DataRequired()])
    fecha_nacimiento    = IntegerField('fecha_nacimiento',validators=[DataRequired()], format='%Y-%m-%d')
    pais                = StringField('pais', validators=[DataRequired(), Length(min=1, max=50)])
    numero_celular      = IntegerField('numero_celular',validators=[DataRequired()])
    correo              = EmailField('correo', validators=[DataRequired(), Email()])
    Submit              = SubmitField('Registrarme')


class FormularioLoginAdministrador(FlaskForm):
    correo = StringField('Correo', validators=[DataRequired(message="El correo es obligatorio."),Email(message="Ingresa un correo válido.")])
    contraseña = PasswordField('Contraseña', validators=[DataRequired(message="La contraseña es obligatoria."),Length(min=6, message="La contraseña debe tener al menos 6 caracteres.")])
    submit = SubmitField('Iniciar Sesion')
    
class FormularioRegistroAdministrador(FlaskForm):
    correo = StringField('Correo Electrónico', validators=[InputRequired(), Email()])
    contraseña = PasswordField('Contraseña', validators=[InputRequired()])
    confirmar_contraseña = PasswordField('Confirmar Contraseña', validators=[DataRequired(message="La confirmación de la contraseña es obligatoria."),EqualTo('contraseña', message="Las contraseñas no coinciden.")])
    Submit = SubmitField("Registrarme")

class FormularioPiesas(FlaskForm):
    nombre_pieza        = StringField('nombre_pieza', validators=[DataRequired()])
    descripcion_pieza   = StringField('descripcion_pieza', validators=[DataRequired()])
    precio_pieza        = IntegerField('precio_pieza', validators=[DataRequired()])
    cantidad_personas   = IntegerField('cantidad_personas', validators=[DataRequired()])
    imagen_pieza        = StringField('nombre_pieza', validators=[DataRequired()])
    Submit = SubmitField("Añadido")