from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SelectField
from wtforms import HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Optional, EqualTo


class SignupForm(FlaskForm):
    """Form to signup as user in application"""

    # basic details
    first_name = StringField('First Name', [DataRequired(message='Please provide your first name')])
    last_name = StringField('Last Name', [DataRequired(message='Please provide your last name')])
    email = EmailField('Email', [Email(message='Not a valid email address'), Optional()])

    # login details
    username = StringField('Username', [DataRequired(),
                                        Length(min=6,
                                               message='Your username should be minimum 6 characters')])
    user_type = SelectField('Employee Type', [DataRequired()], choices=[('Administrator', 'admin'),
                                                                        ('User', 'user')])
    password = PasswordField('Password', [DataRequired(message='Please enter a password'),
                                          Length(min=8,
                                                 message='Password should be at least 8 characters')])
    confirm_pass = PasswordField('ConfirmPassword', [EqualTo('password',
                                                             message='Passwords must match')])

    # recaptcha = RecaptchaField()
    submit = SubmitField('Sign up')


class LoginForm(FlaskForm):
    """Form to sign in to application"""

    username = StringField('Username', [DataRequired(message='Please enter a username')])
    password = PasswordField('Password', [DataRequired(message='Please enter a password')])
    next = HiddenField('Next Value')

    submit = SubmitField('Login')
