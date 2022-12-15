from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, DateField
from wtforms import RadioField, IntegerField, HiddenField, SubmitField
from wtforms import FormField, FieldList
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from .models import Fields, Lands


class FieldsForm(FlaskForm):
    """form to enter field information as part of FormField"""

    location = SelectField('Location', [DataRequired()], choices=[('tgudi', 'Thozuthalangudi'),
                                                                  ('pallachi', 'Pallachi'),
                                                                  ('potteri', 'Potteri'),
                                                                  ('pokonanthoki', 'Pokananthoki'),
                                                                  ('mannamuti', 'Mannamutti'),
                                                                  ('none', 'Not Applicable')],
                           default='tgudi')
    field_extent = DecimalField('Extent (Acres)', [DataRequired()], places=1, rounding=None, default=0.0)
    # nickname = StringField('Nickname', [DataRequired()])


class LandsForm(FlaskForm):
    """form to enter land information as part of FieldList and FormField"""

    extent = DecimalField('Extent', [DataRequired()], places=1, rounding=None, default=0.0)
    geotag = StringField('GeoTag', [Optional()])
    owner = StringField('Owner', [Optional()])
    survey = StringField('Survey #', [Optional()])
    deed = StringField('Deed #', [Optional()])


class FieldEntry(FlaskForm):
    """form to enter field information in html page"""

    fields = FormField(FieldsForm, default=lambda: Fields())
    field_lands = FieldList(FormField(LandsForm, default=lambda: Lands()))

    submit = SubmitField('Add Field')


class SelectFieldLocation(FlaskForm):
    """modify field information by adding lands to given field"""

    location = SelectField('Location', [DataRequired()], choices=[('tgudi', 'Thozuthalangudi'),
                                                                  ('pallachi', 'Pallachi'),
                                                                  ('potteri', 'Potteri'),
                                                                  ('pokonanthoki', 'Pokananthoki'),
                                                                  ('mannamuti', 'Mannamutti'),
                                                                  ('none', 'Not Applicable')],
                           default='tgudi')

    submit = SubmitField('Select Field Location')


class LandEntry(FlaskForm):
    """form to enter land info separately from field info"""

    field_location = StringField('Location', [DataRequired()])
    field_extent = StringField('Extent (Acres)', [DataRequired()])

    field_lands = FieldList(FormField(LandsForm, default=lambda: Lands()))

    submit = SubmitField('Add Land(s) to Field')


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

    submit = SubmitField('Add Sowing Data')


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

