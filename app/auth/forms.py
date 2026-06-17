from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField(
        "Usuario",
        validators=[DataRequired(), Length(min=3, max=50)],
    )
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(), Length(min=8, max=128)],
    )
    remember_me = BooleanField("Recordarme")
    submit = SubmitField("Iniciar sesión")
