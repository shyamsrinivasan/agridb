from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, DecimalField, DateField
from wtforms import RadioField, IntegerField, HiddenField, SubmitField
from wtforms import FormField, FieldList
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from .models import Fields, Lands, Yields, Accounts


class FieldsForm(FlaskForm):
    """form to enter field information as part of FormField"""

    location = SelectField('Location', [DataRequired()], choices=[('tgudi', 'Thozuthalangudi'),
                                                                  ('pallachi', 'Pallachi'),
                                                                  ('potteri', 'Potteri'),
                                                                  ('pokonanthoki', 'Pokananthoki'),
                                                                  ('mannamuti', 'Mannamutti'),
                                                                  ('trichy-home1', 'Home 1'),
                                                                  ('trichy-home2', 'Home 2'),
                                                                  ('house-yard', 'Therazhundhur'),
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
                                                                  ('trichy-home1', 'Home 1'),
                                                                  ('trichy-home2', 'Home 2'),
                                                                  ('house-yard', 'Therazhundhur'),
                                                                  ('none', 'Not Applicable')],
                           default='tgudi')

    submit = SubmitField('Select Field Location')


class LandEntry(FlaskForm):
    """form to enter land info separately from field info"""

    location = StringField('Location', [DataRequired()])
    field_extent = StringField('Extent (Acres)', [DataRequired()])

    field_lands = FieldList(FormField(LandsForm, default=lambda: Lands()))

    submit = SubmitField('Add Land(s) to Field')


class RemoveFields(FlaskForm):
    """remove all fields(and lands) from given location"""

    submit = SubmitField('Remove all lands/fields from Location')


class RemoveLand(FlaskForm):
    """remove specific lands from given location/field"""
    location = SelectField('Location', [DataRequired()], choices=[('tgudi', 'Thozuthalangudi'),
                                                                  ('pallachi', 'Pallachi'),
                                                                  ('potteri', 'Potteri'),
                                                                  ('pokonanthoki', 'Pokananthoki'),
                                                                  ('mannamuti', 'Mannamutti'),
                                                                  ('trichy-home1', 'Home 1'),
                                                                  ('trichy-home2', 'Home 2'),
                                                                  ('house-yard', 'Therazhundhur'),
                                                                  ('none', 'Not Applicable')],
                           default='none')
    land_id = StringField('Land ID', [DataRequired(message='provide comma separated land ids to remove')])
    submit = SubmitField('Remove all lands from Location')


class SowDetails(FlaskForm):
    """seed information"""

    field_area = DecimalField('Area sown (acres)', [DataRequired(message='area in acres required')])
    variety = StringField('Seed variety', [DataRequired(message='Seed variety required')])
    bags = IntegerField('Seed bags sown', [DataRequired(message='Should be integer less than 9999'),
                                           NumberRange(max=9999, message='should be less than 9999')],
                        default=0)
    duration = IntegerField('Typical Crop Duration (days)',
                            [DataRequired(message='Duration in days required'),
                             NumberRange(min=0, max=200,
                                         message='Crop duration should be < 200 days')],
                            default=120)


class SowingEntry(FlaskForm):
    """form to enter owing information"""

    season = SelectField('Season', [DataRequired()],
                         choices=[('summer', 'Kuruvai'),
                                  ('monsoon', 'Thaaladi'),
                                  ('summer', 'Summer'),
                                  ('winter', 'Winter'),
                                  ('other', 'Others')],
                         default='summer')
    location = SelectField('Location', [DataRequired()], choices=[('tgudi', 'Thozuthalangudi'),
                                                                  ('pallachi', 'Pallachi'),
                                                                  ('potteri', 'Potteri'),
                                                                  ('pokonanthoki', 'Pokananthoki'),
                                                                  ('mannamuti', 'Mannamutti'),
                                                                  ('trichy-home1', 'Home 1'),
                                                                  ('trichy-home2', 'Home 2'),
                                                                  ('house-yard', 'Therazhundhur'),
                                                                  ('none', 'Not Applicable')],
                           default='tgudi')
    sowing_date = DateField('Date Sown', [DataRequired(message='Date of sowing required')])

    sow_info = FormField(SowDetails)

    submit = SubmitField('Add Sowing Data')


class SowChangeForm(FlaskForm):
    """sow change/remove/review form"""

    season = SelectField('Season', [DataRequired()],
                         choices=[('summer', 'Kuruvai'),
                                  ('monsoon', 'Thaaladi'),
                                  ('summer', 'Summer'),
                                  ('winter', 'Winter'),
                                  ('other', 'Others')],
                         default='summer')
    location = SelectField('Location', [DataRequired(message='Location is required')],
                           choices=[('tgudi', 'Thozuthalangudi'),
                                    ('pallachi', 'Pallachi'),
                                    ('potteri', 'Potteri'),
                                    ('pokonanthoki', 'Pokananthoki'),
                                    ('mannamuti', 'Mannamutti'),
                                    ('trichy-home1', 'Home 1'),
                                    ('trichy-home2', 'Home 2'),
                                    ('house-yard', 'Therazhundhur'),
                                    ('none', 'Not Applicable')],
                           default='tgudi')
    sowing_date = DateField('Date Sown', [DataRequired(message='Date of sowing required')])

    sow_info = FormField(SowDetails)
    option = RadioField('Choose option', [DataRequired()], choices=[('change', 'Change Data'),
                                                                    ('remove', 'Remove Data')],
                        default='change')

    submit = SubmitField('Change/Remove Sowing Data')


class YieldForm(FlaskForm):
    """form for yield information"""

    # id = db.Column(db.Integer, primary_key=True)
    # sowing_id = db.Column(db.Integer, db.ForeignKey('sowing.id', onupdate='CASCADE',
    #                                                 ondelete='CASCADE'), index=True)
    harvest_date = DateField('Harvested on', [DataRequired(message='Harvest date required')])
    sell_date = DateField('Sold on', [Optional()])
    bags = IntegerField('# Bags', [DataRequired(message='# bags sold'),
                                   NumberRange(max=9999, message='# bags cannot be over 9999')],
                        default=1)
    bag_weight = DecimalField('Kg/bag', [DataRequired(message='Weight of one bag')])
    bag_rate = DecimalField('Rupees/bag', [DataRequired(message='Amount per bag')])
    buyer = StringField('Sold to', [DataRequired(message='give buyer name'),
                                    Length(max=15, message='Should be < 15 characters')])


class YieldEntryForm(FlaskForm):
    """form to enter yield information"""

    season = RadioField('Season', [DataRequired()],
                        choices=[('summer', 'Kuruvai'),
                                 ('monsoon', 'Thaaladi'),
                                 ('summer', 'Summer'),
                                 ('winter', 'Winter'),
                                 ('other', 'Others')],
                        default='summer')
    year = StringField('Year', [Length(message='year should be four digits', min=4, max=4),
                                DataRequired(message='enter year of sowing')])
    location = StringField('location', [DataRequired(message='location of field required')])
    yields = FieldList(FormField(YieldForm), default=lambda: Yields())

    submit = SubmitField('Enter Yield Data for Season')


class YieldChangeForm(FlaskForm):
    """form to review and change yield information"""

    season = SelectField('Season', [DataRequired()],
                         choices=[('summer', 'Kuruvai'),
                                  ('monsoon', 'Thaaladi'),
                                  ('summer', 'Summer'),
                                  ('winter', 'Winter'),
                                  ('other', 'Others')],
                         default='summer')
    location = SelectField('Location', [DataRequired(message='location of field required')],
                           choices=[('tgudi', 'Thozuthalangudi'),
                                    ('pallachi', 'Pallachi'),
                                    ('potteri', 'Potteri'),
                                    ('pokonanthoki', 'Pokananthoki'),
                                    ('mannamuti', 'Mannamutti'),
                                    ('trichy-home1', 'Home 1'),
                                    ('trichy-home2', 'Home 2'),
                                    ('house-yard', 'Therazhundhur'),
                                    ('none', 'Not Applicable')],
                           default='tgudi')
    yields = FormField(YieldForm)

    option = RadioField('Choose option', [DataRequired()], choices=[('change', 'Change Data'),
                                                                    ('remove', 'Remove Data')],
                        default='change')

    submit = SubmitField('Change/Remove Yield Data')


class YieldSowView(FlaskForm):
    """enter information to view yield and/or sow"""

    year = StringField('Year', [Length(message='year should be a four digits', min=4, max=4),
                                DataRequired(message='enter year of sowing')])
    season = SelectField('Season', [DataRequired()],
                         choices=[('summer', 'Kuruvai'),
                                  ('monsoon', 'Thaaladi'),
                                  ('summer', 'Summer'),
                                  ('winter', 'Winter'),
                                  ('other', 'Others'),
                                  ('full_year', 'Full Year'),
                                  ('all_data', 'All Data')],
                         default='summer')
    choice = SelectField('Type', [Optional()], choices=[('yield', 'Yield'),
                                                        ('sow', 'Sowing'),
                                                        ('both', 'Both')])
    submit = SubmitField('View Data')


class YieldSowIDEntry(FlaskForm):
    """form to enter id of yield/sow data to change or delete"""

    option = SelectField('Edit Choice', choices=[('yield', 'Yield ID'),
                                                 ('sow', 'Sow ID')],
                         default='sow')
    desired_id = IntegerField('Sow/Yield ID',
                              [DataRequired(message='Yield/Sow ID required')])
    submit = SubmitField('Show Data to Change/Remove')


class EquipmentEntry(FlaskForm):
    """form to enter equipment information"""

    type = SelectField('Machinery Type', choices=[('motorbike', 'Motor Cycle'),
                                                  ('pumps', 'Water Pump'),
                                                  ('sprayer', 'Battery Sprayer'),
                                                  ('tractor', 'Tractor'),
                                                  ('transplanter', 'Transplanter')],
                       default='transplanter')
    nickname = StringField('Nickname', [DataRequired(message='Nickname for equipment required'),
                                        Length(max=10, message='Should be < 10 characters')])
    geotag = StringField('GeoTag', [Optional()])
    location = SelectField('Location', [DataRequired()], choices=[('tgudi', 'Thozuthalangudi'),
                                                                  ('pallachi', 'Pallachi'),
                                                                  ('potteri', 'Potteri'),
                                                                  ('pokonanthoki', 'Pokananthoki'),
                                                                  ('mannamuti', 'Mannamutti'),
                                                                  ('trichy-home1', 'Home 1'),
                                                                  ('trichy-home2', 'Home 2'),
                                                                  ('house-yard', 'Therazhundhur'),
                                                                  ('none', 'Not Applicable')],
                           default='tgudi')
    last_service = DateField('Last Service on', [Optional()])

    submit = SubmitField('Add Equipment')


class EquipmentView(FlaskForm):
    """view equipment given specific type"""
    type = SelectField('Machinery Type', choices=[('motorbike', 'Motor Cycle'),
                                                  ('pumps', 'Water Pump'),
                                                  ('sprayer', 'Battery Sprayer'),
                                                  ('tractor', 'Tractor'),
                                                  ('transplanter', 'Transplanter'),
                                                  ('all', 'All Types')],
                       default='transplanter')

    submit = SubmitField('View Equipment(s)')


class SeedForm(FlaskForm):
    """enter seed varieties"""

    # file = FileField('Details File',
    #                  [Regexp(r'^[\w,\s-]+\.xlsx$',
    #                          message='Only Excel files are accepted')])
    file = FileField('Details File', [Optional(),
                                      FileAllowed(['xls',
                                                   'xlsx'],
                                                  message='Excel file only')])
    submit = SubmitField('Add Seed Variety from File')


class SeedSelectForm(FlaskForm):
    """select type of seeds to view"""
    seed_type = SelectField('Seeds for', [DataRequired()], choices=[('paddy', 'Rice'),
                                                                    ('veggies', 'Vegetables'),
                                                                    ('flowers', 'Flowers'),
                                                                    ('pulses', 'Pulses'),
                                                                    ('all', 'All Available')],
                            default='paddy')
    season = SelectField('Duration', choices=[], coerce=str)
    disease_resistance = SelectField('Disease Resistance', choices=[], coerce=str)
    pest_resistance = SelectField('Pest Resistance', choices=[], coerce=str)
    submit = SubmitField('Show Seeds')


class AccountingForm(FlaskForm):
    """capture all details in accounts table"""

    category = SelectField('Category', [DataRequired()], choices=[('labour', 'Labour'),
                                                                  ('food', 'Food'),
                                                                  ('rental', 'Rental'),
                                                                  ('repair', 'Repair'),
                                                                  ('maintain', 'Maintenance'),
                                                                  ('fuel', 'Fuel'),
                                                                  ('seeds', 'Seeds'),
                                                                  ('fertilizer', 'Fertilizer'),
                                                                  ('pesticides', 'Pesticides'),
                                                                  ('herbicides', 'Herbicides'),
                                                                  ('sale', 'Sale')],
                           default='labour')
    operation = SelectField('Operation', [DataRequired()],
                            choices=[('field preparation', 'Field Prep'),
                                     ('sowing', 'Sowing'),
                                     ('transplanting', 'Transplanting'),
                                     ('spraying', 'Spraying'),
                                     ('field maintenance', 'Field Maintanance'),
                                     ('weeding', 'Weeding'),
                                     ('harvesting', 'Harvest'),
                                     ('supplies', 'Supplies'),
                                     ('equipments', 'Equipments')],
                            default='field preparation')
    item = StringField('Description', [Optional()])
    rate = DecimalField('Rate', [Optional()], places=2, rounding=None, default=0.00)
    quantity = DecimalField('Quantity', [Optional()], places=1, rounding=None, default=1.0)
    # cost = DecimalField('Cost', [Optional()], places=1, rounding=None, default=1.0)
    # submit = SubmitField('Add Expense to Database')


class AccountEntryForm(FlaskForm):
    """form to enter expense information"""

    date = DateField('Date', [DataRequired()])
    type = RadioField('Accounting Type', [Optional()], choices=[('expense', 'Expense'),
                                                                ('income', 'Income')],
                      default='expense')
    field = SelectField('Location', coerce=str)
    account = FieldList(FormField(AccountingForm, default=lambda: Accounts()))

    submit = SubmitField('Add Income(s)/Expense(s)')


class AccountSearchCategoryForm(FlaskForm):
    """enter category to search account with"""

    search_by = RadioField('Search Using', choices=[('location', 'Location'),
                                                    ('expense', 'Expense'),
                                                    ('income', 'Income'),
                                                    ('date', 'Date'),
                                                    ('month', 'Month'),
                                                    ('category', 'Category'),
                                                    ('operation', 'Operation')],
                           default='location')
    submit = SubmitField('Search Records')

