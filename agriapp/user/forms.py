from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SelectField
from wtforms import HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Optional, EqualTo


class SignupForm(FlaskForm):
    """Form to signup as user in application"""

    # basic details
    firstname = StringField('First Name', [DataRequired(message='Please provide your first name')])
    lastname = StringField('Last Name', [DataRequired(message='Please provide your last name')])

    # login details
    username = StringField('Username', [DataRequired(),
                                        Length(min=6,
                                               message='Your username should be minimum 6 characters')])
    type = SelectField('Employee Type', [DataRequired()], choices=[('admin', 'Admin'),
                                                                   ('user', 'User')], default='user')
    password = PasswordField('Password', [DataRequired(message='Please enter a password'),
                                          Length(min=8,
                                                 message='Password should be at least 8 characters')])
    confirm_pass = PasswordField('Confirm Password', [EqualTo('password',
                                                              message='Passwords must match')])

    # recaptcha = RecaptchaField()
    submit = SubmitField('Sign up')


class LoginForm(FlaskForm):
    """Form to sign in to application"""

    username = StringField('Username', [DataRequired(message='Please enter a username')])
    password = PasswordField('Password', [DataRequired(message='Please enter a password')])
    next = HiddenField('Next Value')

    submit = SubmitField('Login')


class ChangePassword(FlaskForm):
    """change password form"""
    old_pass = PasswordField('Old Password', [DataRequired(message='Please enter old password'),
                                              Length(min=8,
                                                     message='Password should be at least 8 characters')])
    password = PasswordField('Password', [DataRequired(message='Please enter a password'),
                                          Length(min=8,
                                                 message='Password should be at least 8 characters')])
    confirm_pass = PasswordField('Confirm Password',
                                 [EqualTo('password',
                                          message='Passwords must match')])
    submit = SubmitField('Change password')
