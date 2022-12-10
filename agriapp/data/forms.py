from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField
from wtforms import HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class FieldEntry(FlaskForm):
    """form to enter field information"""

    geotag = StringField('GeoTag', [Optional()])
    location = SelectField('Employee Type', [DataRequired()], choices=[('tgudi', 'Thozuthalangudi'),
                                                                       ('pallachi', 'Pallachi'),
                                                                       ('potteri', 'Potteri'),
                                                                       ('pokonanthoki', 'Pokananthoki'),
                                                                       ('mannamuti', 'Mannamutti')], default='user')
    extent = DecimalField('Extent', [Optional()], places=1, rounding=None, default=0.0)
    nickname = StringField('Nickname', [DataRequired()])
    owner = StringField('Owner', [Optional()])
    survey = StringField('Survey #', [Optional()])
    deed = StringField('Deed #', [Optional()])

    submit = SubmitField('Add Field')


class YieldEntry(FlaskForm):
    """form to yield information"""


class EquipmentEntry(FlaskForm):
    """form to enter equipment information"""


class ExpenseEntry(FlaskForm):
    """form to enter expense information"""

