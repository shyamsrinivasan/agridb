import datetime
import numpy as np
import pandas as pd

from agriapp import db
from datetime import timedelta
from datetime import datetime as dt


class Fields(db.Model):
    """table of basic fields with locations"""

    __tablename__ = "fields"
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.Enum('tgudi', 'pallachi', 'potteri', 'pokonanthoki',
                                 'mannamuti', 'trichy-home1', 'trichy-home2',
                                 'house-yard', name='field_location'),
                         default='tgudi',
                         nullable=False, index=True)
    field_extent = db.Column(db.Float)

    field_lands = db.relationship('Lands', uselist=True)

    # association table many-to-many relations
    # yield_info = db.relationship('Yields', secondary="fieldlink")
    # sow_info = db.relationship('Sowing', secondary="fieldlink")
    # accounts = db.relationship('Accounts', secondary="accountlink")
    yields = db.relationship('Yields', foreign_keys="[Yields.location]", uselist=True)
    sow_info = db.relationship('Sowing', foreign_keys="[Sowing.location]", uselist=True)
    equipment_info = db.relationship('Equipment', foreign_keys="[Equipment.location]")
    accounts = db.relationship('Accounts', foreign_keys="[Accounts.location_id]")

    def __repr__(self):
        return f"Fields(id={self.id!r}, location={self.location!r}, " \
               f"extent={self.field_extent!r})"

    def is_present(self):
        field_obj = db.session.query(Fields).filter(Fields.location == self.location).first()
        if field_obj and field_obj is not None:
            return True
        else:
            return False


class Lands(db.Model):
    """table of all formal lands (uses fields as FK)"""

    __tablename__ = "lands"
    id = db.Column(db.Integer, primary_key=True)
    field_location = db.Column(db.Enum('tgudi', 'pallachi', 'potteri', 'pokonanthoki',
                                       'mannamuti', 'trichy-home1', 'trichy-home2',
                                       'house-yard', name='field_location'),
                               db.ForeignKey('fields.location', ondelete='CASCADE',
                                             onupdate='CASCADE'))
    extent = db.Column(db.Float)
    geotag = db.Column(db.String(15))
    owner = db.Column(db.String(30))
    survey = db.Column(db.String(10))
    deed = db.Column(db.String(10))

    def __repr__(self):
        return f"Lands(id={self.id!r}, location={self.field_location!r}, " \
               f"extent={self.extent!r}, survey={self.survey!r}, deed={self.deed!r})"

    def survey_present(self):
        survey_test = db.session.query(Lands).filter(Lands.field_location == self.field_location,
                                                     Lands.survey == self.survey).all()
        if survey_test and survey_test is not None:
            return True
        else:
            return False

    def deed_present(self):
        deed_test = db.session.query(Lands).filter(Lands.field_location == self.field_location,
                                                   Lands.deed == self.deed).all()
        if deed_test and deed_test is not None:
            return True
        else:
            return False

    def survey_deed_present(self):
        test_obj = db.session.query(Lands).filter(Lands.field_location == self.field_location,
                                                  Lands.survey == self.survey,
                                                  Lands.deed == self.deed).all()
        if test_obj and test_obj is not None:
            return True
        else:
            return False


class Sowing(db.Model):
    __tablename__ = "sowing"

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(4), nullable=False, index=True)
    season = db.Column(db.String(10), nullable=False, index=True)
    location = db.Column(db.Enum('tgudi', 'pallachi', 'potteri', 'pokonanthoki',
                                 'mannamuti', 'trichy-home1', 'trichy-home2',
                                 'house-yard', name='field_location'),
                         db.ForeignKey('fields.location', onupdate='CASCADE',
                                       ondelete='CASCADE'),
                         index=True)
    variety = db.Column(db.String(10))
    field_area = db.Column(db.Float)
    bags = db.Column(db.Integer)
    sowing_date = db.Column(db.Date)
    duration = db.Column(db.Integer, nullable=False, default=110)
    expected_harvest = db.Column(db.Date)

    # yield_info = db.relationship('Yields', foreign_keys="[Yields.sowing_id]",
    #                              back_populates='sow_info',
    #                              cascade='all, delete', uselist=False)
    # yields = db.relationship('Yields', secondary="fieldlink")
    # sow_info = db.relationship('Sowing', secondary="fieldlink")

    def calculate_harvest(self):
        # self.expected_harvest = self.sowing_date + timedelta(days=int(days))
        if type(self.sowing_date) == datetime.datetime:
            if type(self.duration) == int:
                self.expected_harvest = self.sowing_date + timedelta(days=self.duration)
            else:
                self.expected_harvest = self.sowing_date + timedelta(days=int(self.duration))
        else:
            self.expected_harvest = None

    def __init__(self, **kwargs):
        super(Sowing, self).__init__(**kwargs)
        self.calculate_harvest()

    def compare_change_values(self, values_dict):
        """compare to check values and change different values"""
        if values_dict['season'] != self.season:
            self.season = values_dict['season']

        flag, change_values = False, False
        if values_dict['sowing_date'] != self.sowing_date.strftime('%Y-%m-%d'):
            self.sowing_date = dt.strptime(values_dict['sowing_date'], '%Y-%m-%d')
            self.year = dt.strptime(values_dict['sowing_date'], '%Y-%m-%d').year
            flag = True
            change_values = True

        if float(values_dict['sow_info-field_area']) != self.field_area:
            self.field_area = values_dict['sow_info-field_area']
            change_values = True

        if values_dict['sow_info-variety'] != self.variety:
            self.variety = values_dict['sow_info-variety']
            change_values = True

        if int(values_dict['sow_info-bags']) != self.bags:
            self.bags = values_dict['sow_info-bags']
            change_values = True

        if int(values_dict['sow_info-duration']) != self.duration:
            self.duration = int(values_dict['sow_info-duration'])
            flag = True

        # recalculate harvest date
        if flag:
            self.calculate_harvest()

        return change_values

    def __repr__(self):
        return f"Sowing(id={self.id!r}, year={self.year!r}, season={self.season!r}, " \
               f"location={self.location!r}, variety={self.variety!r}" \
               f"bags={self.bags!r}, sowed_on={self.sowing_date!r}, " \
               f"harvest={self.expected_harvest!r})"


class Yields(db.Model):
    __tablename__ = "yield"

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(4), nullable=False, index=True)
    season = db.Column(db.String(10), nullable=False, index=True)
    location = db.Column(db.Enum('tgudi', 'pallachi', 'potteri', 'pokonanthoki',
                                 'mannamuti', 'trichy-home1', 'trichy-home2',
                                 'house-yard', name='field_location'),
                         db.ForeignKey('fields.location', onupdate='CASCADE',
                                       ondelete='CASCADE'),
                         index=True)
    # sowing_id = db.Column(db.Integer, db.ForeignKey('sowing.id', onupdate='CASCADE',
    #                                                 ondelete='CASCADE'), index=True)
    harvest_date = db.Column(db.Date)
    sell_date = db.Column(db.Date)

    bags = db.Column(db.Integer, nullable=False, default=0)
    bag_weight = db.Column(db.Float)
    bag_rate = db.Column(db.Float)
    buyer = db.Column(db.String(15))
    income = db.Column(db.Float)
    weight = db.Column(db.Float)

    # yield_info = db.relationship('YieldEntry')
    # sow_info = db.relationship('Sowing', foreign_keys="[Yields.sowing_id]",
    #                            back_populates='yield_info',
    #                            cascade='all, delete', uselist=False)
    sow_info = db.relationship('Sowing', secondary="fieldlink")

    def __init__(self, **kwargs):
        super(Yields, self).__init__(**kwargs)
        self.set_weight()
        self.set_income()

    def set_income(self):
        self.income = self.bags * self.bag_rate

    def set_weight(self):
        """yield in tonnes"""
        self.weight = self.bags * self.bag_weight / 1000

    def compare_change_values(self, values_dict):
        """compare to check values and change different values"""
        if values_dict['season'] != self.season:
            self.season = values_dict['season']

        flag, flag2, change_values = False, False, False
        if values_dict['yields-harvest_date'] != self.harvest_date.strftime('%Y-%m-%d'):
            self.harvest_date = dt.strptime(values_dict['yields-harvest_date'], '%Y-%m-%d')
            self.year = dt.strptime(values_dict['yields-harvest_date'], '%Y-%m-%d').year
            flag = True
            change_values = True

        if values_dict['yields-sell_date'] != self.sell_date.strftime('%Y-%m-%d'):
            self.sell_date = dt.strptime(values_dict['yields-sell_date'], '%Y-%m-%d')

        if int(values_dict['yields-bags']) != self.bags:
            self.bags = int(values_dict['yields-bags'])
            change_values = True
            flag = True
            flag2 = True

        if float(values_dict['yields-bag_weight']) != self.bag_weight:
            self.bag_weight = float(values_dict['yields-bag_weight'])
            change_values = True
            flag = True

        if float(values_dict['yields-bag_rate']) != self.bag_rate:
            self.bag_rate = float(values_dict['yields-bag_rate'])
            change_values = True
            flag2 = True

        if values_dict['yields-buyer'] != self.buyer:
            self.buyer = values_dict['yields-buyer']

        # recalculate harvest weight
        if flag:
            self.set_weight()

        # recalculate harvest income
        if flag2:
            self.set_income()

        return change_values

    def __repr__(self):
        return f"Yield(id={self.id!r}, location={self.location!r}, bags={self.bags!r}, " \
               f"bag_rate={self.bag_rate!r}, buyer={self.buyer!r}, year={self.year!r}, " \
               f"season={self.season!r})"


class FieldSowYieldLink(db.Model):
    """association table linking field, yield and sowing"""

    __tablename__ = 'fieldlink'

    # field_id = db.Column(db.Integer, db.ForeignKey('fields.id'), primary_key=True)
    sow_id = db.Column(db.Integer, db.ForeignKey('sowing.id'), primary_key=True)
    yield_id = db.Column(db.Integer, db.ForeignKey('yield.id'), primary_key=True)


class Equipment(db.Model):
    """all equipments (including water pumps)"""

    __tablename__ = "equipments"

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(10), unique=True, nullable=False, index=True)
    type = db.Column(db.Enum('motorbike', 'pumps', 'sprayer', 'tractor', 'transplanter',
                             name='equipment_type'), default='transplanter',
                     nullable=False)
    geotag = db.Column(db.String(30))
    location = db.Column(db.Enum('tgudi', 'pallachi', 'potteri', 'pokonanthoki',
                                 'mannamuti', 'trichy-home1', 'trichy-home2',
                                 'house-yard', name='field_location'),
                         db.ForeignKey('fields.location', ondelete='CASCADE',
                                       onupdate='CASCADE'))
    last_service = db.Column(db.Date, onupdate=db.func.now())

    def __repr__(self):
        return f"Equipments(id={self.id!r}, type={self.type!r}, location={self.location!r}, " \
               f"nickname={self.nickname!r}," \
               f"serviced_on={self.last_service!r})"

    def check_equipment_nickname(self):
        """check if given nickname exists in db"""
        existing_obj = db.session.query(Equipment).filter(Equipment.nickname == self.nickname).first()
        if existing_obj and existing_obj is not None:
            return True
        else:
            return False


class SeedVariety(db.Model):
    """table of seed varieties"""
    __tablename__ = "variety"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False, index=True)
    duration = db.Column(db.Integer, nullable=False, index=True)
    seasons = db.Column(db.String(15), index=True)
    average_yield = db.Column(db.String(6))     # Kg/ha
    grain_weight = db.Column(db.Float)          # g/1000 grain
    disease_resistance = db.Column(db.String(40))
    pest_resistance = db.Column(db.String(40))
    habit = db.Column(db.String(40))
    grain_type = db.Column(db.String(15))
    # grain - paddy/millets/grams/others?
    grain = db.Column(db.String(10), default='paddy')
    # yes/no fields
    ruling_variety = db.Column(db.String(3))
    hybrid = db.Column(db.String(3))

    def __init__(self, data: pd.Series):
        self.name = data['name']
        if data['duration'] is not np.nan:
            self.duration = int(data['duration'])

        if 'season' in data.index:
            if data['season'] is not np.nan:
                self.seasons = data['season']
        elif 'seasons' in data.index:
            if data['seasons'] is not np.nan:
                self.seasons = data['seasons']

        if data['average_yield'] is not np.nan:
            self.average_yield = data['average_yield']

        if data['grain_weight'] is not np.nan:
            self.grain_weight = data['grain_weight']

        self.disease_resistance = ''
        if data['disease_resistance'] is not np.nan:
            self.disease_resistance = data['disease_resistance']
            if type(data['disease_resistance']) is np.ndarray or type(data['disease_resistance']) is list:
                self.disease_resistance = [val for val in data['disease_resistance'] if val]

        self.pest_resistance = ''
        if data['pest_resistance'] is not np.nan:
            self.pest_resistance = data['pest_resistance']
            if type(data['pest_resistance']) is np.ndarray or type(data['pest_resistance']) is list:
                self.pest_resistance = [val for val in data['pest_resistance'] if val]

        if data['habit'] is not np.nan:
            self.habit = data['habit']

        if data['grain_type'] is not np.nan:
            self.grain_type = data['grain_type']

        if data['grain'] is not np.nan:
            self.grain = data['grain']

        if data['ruling_variety'] is not np.nan:
            self.ruling_variety = data['ruling_variety']

        if data['hybrid'] is not np.nan:
            self.hybrid = data['hybrid']

    def check_variety_name(self):
        seed_obj = db.session.query(SeedVariety).filter(SeedVariety.name == self.name).first()
        if seed_obj and seed_obj is not None:
            return True
        else:
            return False

    def is_present(self):
        seed_obj = db.session.query(SeedVariety).filter(SeedVariety.name == self.name,
                                                        SeedVariety.grain == self.grain,
                                                        SeedVariety.pest_resistance ==
                                                        self.pest_resistance,
                                                        SeedVariety.disease_resistance ==
                                                        self.disease_resistance).first()
        if seed_obj and seed_obj is not None:
            return True
        else:
            return False

    def __repr__(self):
        return f"SeedVariety(id={self.id!r}, name={self.name!r}, " \
               f"duration={self.duration!r}, " \
               f"seasons={self.seasons!r}, average_yield={self.average_yield!r}" \
               f"grain_weight={self.grain_weight!r}, habit={self.habit!r}, " \
               f"grain_type={self.grain_type!r}," \
               f"grain={self.grain!r}, ruling_variety={self.ruling_variety!r}," \
               f"hybrid={self.hybrid!r}, disease_resistance={self.disease_resistance!r}," \
               f"pest_resistance={self.pest_resistance!r})"


class Accounts(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, db.ForeignKey('entry.id', onupdate='CASCADE', ondelete='CASCADE'),
                         index=True)
    location_id = db.Column(db.Integer, db.ForeignKey('fields.id', onupdate='CASCADE',
                                                      ondelete='CASCADE'),
                            index=True)
    expense_type = db.Column(db.Enum('expense', 'income', name='expense_type'),
                             db.ForeignKey('entry.type'),
                             default='expense', index=True)
    category = db.Column(db.Enum('labour', 'food', 'rental',
                                 'repair', 'maintenance', 'fuel',
                                 'paddy seeds', 'lentil seeds', 'fertilizer',
                                 'pesticides', 'herbicides', 'paddy sale',
                                 'lentil sale',
                                 name='category'),
                         default='labour')
    operation = db.Column(db.Enum('field preparation', 'sowing', 'transplanting',
                                  'spraying', 'field maintenance', 'weeding',
                                  'harvesting', 'supplies', 'equipments',
                                  name='operation'),
                          default='field preparation')
    item = db.Column(db.String(15))
    rate = db.Column(db.Float)
    quantity = db.Column(db.Float)
    cost = db.Column(db.Float)

    # entry = db.relationship('AccountEntry', secondary='accountlink')

    def __init__(self, **kwargs):
        super(Accounts, self).__init__(**kwargs)
        self.set_cost()

    def set_cost(self):
        self.cost = self.rate * self.quantity

    def __repr__(self):
        return f"Account(id={self.id!r}, type={self.expense_type!r}, " \
               f"category={self.category!r}, " \
               f"operation={self.operation!r}, field={self.location_id!r}," \
               f"item={self.item!r}, rate={self.rate!r}, quantity={self.quantity!r}," \
               f"cost={self.cost!r})"


class AccountEntry(db.Model):
    """model containing all expenses in a given list"""

    __tablename__ = 'entry'

    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('fields.id', onupdate='CASCADE',
                                                      ondelete='CASCADE'),
                            index=True)
    date = db.Column(db.Date)
    type = db.Column(db.Enum('expense', 'income', name='expense_type'),
                     default='expense', index=True)

    account = db.relationship('Accounts', secondary='accountlink')

    def __repr__(self):
        return f"Account(id={self.id!r}, type={self.type!r}, date={self.date!r}," \
               f"field={self.location_id!r})"


class AccountsLink(db.Model):
    """Association table between fields and accounts"""

    __tablename__ = 'accountlink'

    # field_id = db.Column(db.Integer, db.ForeignKey('fields.id'), primary_key=True)
    entry_id = db.Column(db.Integer, db.ForeignKey('entry.id'), primary_key=True)
    accounts_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), primary_key=True)


class Measurements:
    def __init__(self, value, imperial=False):
        self.value = value
        self.imperial = imperial
        self.unit = ''

    def __call__(self):
        return self.value


class Temperature(Measurements):
    def __init__(self, temperature, imperial=False):
        super().__init__(temperature, imperial)
        if imperial:
            self.unit = 'F'
        else:
            self.unit = 'C'

    # def __call__(self):
    #     super().__call__()

    def convert_to_imperial(self):
        """convert SI to Imperial units"""
        if not self.imperial:
            self.value = self.value * 1.8 + 32
            self.unit = 'F'
            self.imperial = True

    def convert_to_si(self):
        """convert imperial to SI"""
        if self.imperial:
            self.value = (self.value - 32) / 1.8
            self.unit = 'C'
            self.imperial = False


class Pressure(Measurements):
    def __init__(self, pressure, imperial=False):
        super().__init__(pressure, imperial)
        if imperial:
            self.unit = 'psi'
        else:
            self.unit = 'kPa'

    def convert_to_imperial(self):
        """convert SI to Imperial units"""
        if not self.imperial:
            self.value *= 0.145
            self.unit = 'psi'
            self.imperial = True

    def convert_to_si(self):
        """convert imperial to SI"""
        if self.imperial:
            self.value /= 0.145
            self.unit = 'kPa'
            self.imperial = False


class Humidity(Measurements):
    def __init__(self, humidity):
        super().__init__(humidity)
        self.unit = '%'


class AirEnvironment:
    """All environment variables stored in a single class"""
    def __init__(self, values):
        self.date = values['date']
        self.time = values['time']
        self.temperature = Temperature(values['air_temperature'])   # temperature object
        self.pressure = Pressure(values['pressure'])
        self.humidity = Humidity(values['humidity'])


class SoilMoisture(Measurements):
    def __init__(self, moisture, classification=None):
        super().__init__(moisture)
        self.unit = '%'
        self.classification = classification


class SoilpH(Measurements):
    def __init__(self, pHvalue, classification=None):
        super().__init__(pHvalue)
        self.unit = ''
        self.classification = classification


class SoilEnvironment:
    def __init__(self, values):
        self.date = values['date']
        self.time = values['time']
        self.temperature = Temperature(values['soil_temperature'])
        self.moisture = SoilMoisture(values['moisture'])
        self.pH = SoilpH(values['pH'])


class EnviromentalData(db.Model):
    __tablename__ = "envdata"

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime)
    time = db.Column(db.Time, nullable=False)
    temperature = db.Column(db.Float)
    pressure = db.Column(db.Float)
    humidity = db.Column(db.Float)
    rainfall = db.Column(db.Float)
    soil_temperature = db.Column(db.Float)
    soil_moisture = db.Column(db.Float)
    soil_ph = db.Column(db.Float)
    moisture_category = db.Column(db.String(10))
    # location = db.Column(db.String(15))
    # location = db.Column(db.Enum('tgudi', 'pallachi', 'potteri', 'pokonanthoki',
    #                              'mannamuti', 'trichy-home1', 'trichy-home2',
    #                              'house-yard', name='field_location'),
    #                      default='tgudi',
    #                      nullable=False, index=True)
    location_id = db.Column(db.Integer, db.ForeignKey('fields.id', onupdate='CASCADE',
                                                      ondelete='CASCADE'),
                            index=True)

    def __init__(self, data, **kwargs):
        super(EnviromentalData, self).__init__(**kwargs)
        self.year = data.Year
        self.month = data.Month
        self.day = data.Date
        self.temperature = data.Temperature
        self.humidity = data.Humidity
        if hasattr(data, 'Pressure'):
            self.pressure = data.Pressure
        if hasattr(data, 'rainfall'):
            self.rainfall = data.rainfall
        if hasattr(data, 'soil_temperature'):
            self.soil_temperature = db.Column(db.Float)
        if hasattr(data, 'soil_moisture'):
            self.soil_moisture = data.soil_moisture
        if hasattr(data, 'soil_pH'):
            self.soil_ph = db.Column(db.Float)
        if hasattr(data, 'moisture_category'):
            self.moisture_category = data.moisture_category
        self.date = dt(int(data.Year), int(data.Month), int(data.Date),
                       hour=int(data.Hour), minute=int(data.Minute))

    def __repr__(self):
        return f"EnvData(id={self.id!r}, temperature={self.temperature!r}, " \
               f"pressure={self.pressure!r}, humidity={self.humidity!r}," \
               f"rainfall={self.rainfall!r}, soil_temp={self.soil_temperature!r}," \
               f"soil_moisture={self.soil_moisture!r}, soil_ph={self.soil_ph!r})"
