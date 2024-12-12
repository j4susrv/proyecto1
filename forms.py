from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, TextAreaField, IntegerField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo
class FormularioRegistro(FlaskForm):    
    nombre_apellido     = StringField('nombre_apellido', validators=[DataRequired(), Length(min=3, max=50)])
    rut_pasaporte       = StringField('rut',validators=[DataRequired()])
    fecha_nacimiento    = IntegerField('fecha_nacimiento',validators=[DataRequired()], format='%Y-%m-%d')
    pais                = StringField('pais', validators=[DataRequired(), Length(min=1, max=50)])
    numero_celular      = IntegerField('numero_celular',validators=[DataRequired()])
    correo              = EmailField('correo', validators=[DataRequired(), Email()])
    Submit              = SubmitField('Registrarme')


class FormularioRegistroLoginAdministrador(FlaskForm):
    correo = EmailField("Correo", validators=[DataRequired(), Email()])
    contraseña = PasswordField("Contraseña", validators=[DataRequired(), Length(min=6, max=20), EqualTo('confirmar_contraseña', message="Las contraseñas no coinciden.")])
    confirmar_contraseña = PasswordField("Confirmar Contraseña", validators=[DataRequired()])
    submit = SubmitField("Registrarse")
    
