from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, DateField
from wtforms import RadioField, IntegerField, HiddenField, SubmitField
from wtforms import FormField, FieldList
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from .models import Fields


class FieldsForm(FlaskForm):
    """form to enter field information as part of FieldList"""

    geotag = StringField('GeoTag', [Optional()])
    location = SelectField('Location', [DataRequired()], choices=[('tgudi', 'Thozuthalangudi'),
                                                                  ('pallachi', 'Pallachi'),
                                                                  ('potteri', 'Potteri'),
                                                                  ('pokonanthoki', 'Pokananthoki'),
                                                                  ('mannamuti', 'Mannamutti'),
                                                                  ('none', 'Not Applicable')],
                           default='tgudi')
    extent = DecimalField('Extent', [Optional()], places=1, rounding=None, default=0.0)
    nickname = StringField('Nickname', [DataRequired()])
    owner = StringField('Owner', [Optional()])
    survey = StringField('Survey #', [Optional()])
    deed = StringField('Deed #', [Optional()])


class FieldEntry(FlaskForm):
    """form to enter field information in html page"""

    # id = IntegerField('ID', [DataRequired(message='entry id required')])
    fields = FieldList(FormField(FieldsForm, default=lambda: Fields()))

    submit = SubmitField('Add Field')


class YieldEntry(FlaskForm):
    """form to yield information"""

    # id = db.Column(db.Integer, primary_key=True)
    # sowing_id = db.Column(db.Integer, db.ForeignKey('sowing.id', onupdate='CASCADE',
    #                                                 ondelete='CASCADE'), index=True)
    harvest_date = DateField('Harvested on', [DataRequired(message='Date of harvest required')])
    sell_date = DateField('Sold on', [Optional()])

    bags = IntegerField('Bags Harvested', [DataRequired(message='# bags sold'),
                                           NumberRange(max=9999, message='# bags cannot be over 9999')],
                        default=0)
    bag_weight = DecimalField('Weight per bag (Kg)', [DataRequired(message='Weight of each bag')])
    bag_rate = DecimalField('Amount per bag (Rs)', [DataRequired(message='Amount given per bag')])
    buyer = StringField('Sold to', [DataRequired(message='Buyer designation required'),
                                    Length(max=15, message='Should be < 15 characters')])


class EquipmentEntry(FlaskForm):
    """form to enter equipment information"""

    nickname = StringField('Nickname', [DataRequired(message='Nickname for equipment required'),
                                        Length(max=10, message='Should be < 10 characters')])
    type = SelectField(choices=[('motorbike', 'Motor Cycle'),
                                ('pumps', 'Water Pump'),
                                ('sprayer', 'Battery Sprayer'),
                                ('tractor', 'Tractor'),
                                ('transplanter', 'Transplanter')],
                       default='transplanter')
    geotag = StringField('GeoTag', [Optional()])
    location = SelectField('Location', choices=[('tgudi', 'Thozuthalangudi'),
                                                ('pallachi', 'Pallachi'),
                                                ('potteri', 'Potteri'),
                                                ('pokonanthoki', 'Pokananthoki'),
                                                ('mannamuti', 'Mannamutti')],
                           default='tgudi')
    last_service = DateField([Optional()])


class ExpenseEntry(FlaskForm):
    """form to enter expense information"""


class SowingEntry(FlaskForm):
    """form to enter owing information"""

    year = DateField('Year', [DataRequired(message='Enter year of sowing')])
    season = RadioField('Season', choices=[('summer', 'Kuruvai'),
                                           ('monsoon', 'Thaaladi')],
                        default='summer')
    location = SelectField('Location', choices=[('tgudi', 'Thozuthalangudi'),
                                                ('pallachi', 'Pallachi'),
                                                ('potteri', 'Potteri'),
                                                ('pokonanthoki', 'Pokananthoki'),
                                                ('mannamuti', 'Mannamutti')],
                           default='tgudi')
    variety = StringField('Seed variety', [DataRequired(message='Seed variety required')])
    field_area = DecimalField('Area sown (acres)', [DataRequired(message='Enter area in acres')])
    bags = IntegerField('Seed bags sown', [DataRequired(message='# seed bags sown'),
                                           NumberRange(max=9999, message='# bags cannot be over 9999')],
                        default=0)
    sowing_date = DateField('Date Sown', [DataRequired(message='Date of sowing required')])
    duration = IntegerField('Typical Crop Duration (days)',
                            [DataRequired(message='Total crop duration in days required'),
                             NumberRange(min=0, max=200,
                                         message='Crop duration should be < 200 days')],
                            default=120)

