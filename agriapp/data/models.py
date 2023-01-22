import datetime

from agriapp import db
from datetime import timedelta


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

    field_lands = db.relationship('Lands')
    yields = db.relationship('Yields', foreign_keys="[Yields.location]")
    sow_info = db.relationship('Sowing', foreign_keys="[Sowing.location]")
    equipment_info = db.relationship('Equipment', foreign_keys="[Equipment.location]")

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

    # yield_info = db.relationship('Yields', back_populates='sow_info', cascade='all, delete', uselist=False)

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
    # sow_info = db.relationship('Sowing', back_populates='yield_info', cascade='all, delete')

    def __init__(self, **kwargs):
        super(Yields, self).__init__(**kwargs)
        self.set_weight()
        self.set_income()

    def set_income(self):
        self.income = self.bags * self.bag_rate

    def set_weight(self):
        """yield in tonnes"""
        self.weight = self.bags * self.bag_weight / 1000

    def __repr__(self):
        return f"Yield(id={self.id!r}, location={self.location!r}, bags={self.bags!r}, " \
               f"bag_rate={self.bag_rate!r}, buyer={self.buyer!r}, year={self.year!r}, " \
               f"season={self.season!r})"


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
    name = db.Column(db.String(6), nullable=False, index=True)
    duration = db.Column(db.Integer, nullable=False, index=True)
    seasons = db.Column(db.String(15), index=True)
    average_yield = db.Column(db.String(6))     # Kg/ha
    grain_weight = db.Column(db.Float)          # g/1000 grain
    disease_resistance = db.Column(db.String(15))
    pest_resistance = db.Column(db.String(15))
    habit = db.Column(db.String(15))
    grain_type = db.Column(db.String(15))
    # grain - paddy/millets/grams/others?
    grain = db.Column(db.String(10), default='paddy')
    # yes/no fields
    ruling_variety = db.Column(db.String(3))
    hybrid = db.Column(db.String(3))

    def __init__(self, data):
        self.name = data['name']
        self.duration = data['duration']
        self.seasons = data['season']
        self.average_yield = data['average_yield']
        self.grain_weight = data['grain_weight']
        self.disease_resistance = data['disease_resistance']
        self.pest_resistance = data['pest_resistance']
        self.habit = data['habit']
        self.grain_type = data['grain_type']
        self.grain = data['grain']
        self.ruling_variety = data['ruling_variety']
        self.hybrid = data['hybrid']

    def __repr__(self):
        return f"SeedVariety(id={self.id!r}, name={self.name!r}, " \
               f"duration={self.duration!r}, " \
               f"seasons={self.seasons!r}, average_yield={self.average_yield!r}" \
               f"grain_weight={self.grain_weight!r}, habit={self.habit!r}, " \
               f"grain_type={self.grain_type!r}," \
               f"grain={self.grain!r}, ruling_variety={self.ruling_variety!r}," \
               f"hybrid={self.hybrid!r})"


class Accounts(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, db.ForeignKey('entry.id', onupdate='CASCADE', ondelete='CASCADE'),
                         index=True)
    field = db.Column(db.Enum('tgudi', 'pallachi', 'potteri', 'pokonanthoki',
                              'mannamuti', name='field_location'),
                      db.ForeignKey('fields.location', onupdate='CASCADE',
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

    def __init__(self, **kwargs):
        super(Accounts, self).__init__(**kwargs)
        self.set_cost()

    def set_cost(self):
        self.cost = self.rate * self.quantity

    def __repr__(self):
        return f"Account(id={self.id!r}, type={self.expense_type!r}, " \
               f"category={self.category!r}, " \
               f"operation={self.operation!r}, field={self.field!r}" \
               f"item={self.item!r}, rate={self.rate!r}, quantity={self.quantity!r}," \
               f"cost={self.cost!r})"


class AccountEntry(db.Model):
    """model containing all expenses in a given list"""

    __tablename__ = 'entry'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    type = db.Column(db.Enum('expense', 'income', name='expense_type'),
                     default='expense', index=True)

    account = db.relationship('Accounts', foreign_keys="[Accounts.entry_id]")

    def __repr__(self):
        return f"Account(id={self.id!r}, type={self.type!r}, date={self.date!r})"

