from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, SelectField, FileField
from wtforms.validators import DataRequired

class RegisterForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    role = SelectField(choices=[('worker','Worker'),('employer','Employer')])

class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])

class JobForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    description = TextAreaField(validators=[DataRequired()])
    salary = IntegerField()
    category = StringField()
    city = StringField()

class ResumeForm(FlaskForm):
    resume = FileField()
