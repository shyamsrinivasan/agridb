from agriapp import db


class Fields(db.Model):
    """table of basic fields with locations"""

    __tablename__ = "fields"
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.Enum('tgudi', 'pallachi', 'potteri', 'pokonanthoki',
                                 'mannamuti', name='field_location'),
                         default='tgudi',
                         nullable=False, index=True)
    field_extent = db.Column(db.Float)

    field_lands = db.relationship('Lands')

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
                                       'mannamuti', name='field_location'),
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
                                 'mannamuti', name='field_location'),
                         db.ForeignKey('fields.location', onupdate='CASCADE',
                                       ondelete='CASCADE'),
                         index=True)
    variety = db.Column(db.String(10))
    field_area = db.Column(db.Float)
    bags = db.Column(db.Integer)
    sowing_date = db.Column(db.Date)
    expected_harvest = db.Column(db.Date)

    def calculate_harvest(self, days):
        self.expected_harvest = self.sowing_date + days

    def __repr__(self):
        return f"Sowing(id={self.id!r}, year={self.year!r}, season={self.season!r}, " \
               f"location={self.location!r}, variety={self.variety!r}" \
               f"bags={self.bags!r}, sowed_on={self.sowing_date!r}, " \
               f"harvest={self.expected_harvest!r})"


class Equipments(db.Model):
    """all equipments (including water pumps)"""

    __tablename__ = "equipment"

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(10), unique=True, nullable=False, index=True)
    type = db.Column(db.Enum('motorbike', 'pumps', 'sprayer', 'tractor', 'transplanter',
                             name='equipment_type'), default='transplanter',
                     nullable=False)
    geotag = db.Column(db.String(30))
    location = db.Column(db.Enum('tgudi', 'pallachi', 'potteri', 'pokonanthoki',
                                 'mannamuti', 'none', name='field_location'),
                         default='none',
                         nullable=False, index=True)
    last_service = db.Column(db.Date, onupdate=db.func.now())

    def __repr__(self):
        return f"Equipments(id={self.id!r}, type={self.type!r}, location={self.location!r}, " \
               f"nickname={self.nickname!r}," \
               f"serviced_on={self.last_service!r})"


class Yield(db.Model):
    __tablename__ = "yield"

    id = db.Column(db.Integer, primary_key=True)
    sowing_id = db.Column(db.Integer, db.ForeignKey('sowing.id', onupdate='CASCADE',
                                                    ondelete='CASCADE'), index=True)
    harvest_date = db.Column(db.Date)
    sell_date = db.Column(db.Date)

    bags = db.Column(db.Integer, nullable=False, default=0)
    bag_weight = db.Column(db.Float)
    bag_rate = db.Column(db.Float)
    buyer = db.Column(db.String(15))
    income = db.Column(db.Float)
    weight = db.Column(db.Float)

    def set_income(self):
        self.income = self.bags * self.bag_rate

    def set_weight(self):
        """yield in tonnes"""
        self.weight = self.bags * self.bag_weight / 1000

    def __repr__(self):
        return f"Yield(id={self.id!r}, sowing_id={self.sowing_id!r}, bags={self.bags!r}, " \
               f"bag_rate={self.bag_rate!r}, buyer={self.buyer!r})"


class Account(db.Model):
    __tablename__ = "account"

    id = db.Column(db.Integer, primary_key=True)
    field = db.Column(db.Enum('tgudi', 'pallachi', 'potteri', 'pokonanthoki',
                              'mannamuti', name='field_location'),
                      db.ForeignKey('fields.location', onupdate='CASCADE',
                                    ondelete='CASCADE'),
                      index=True)
    type = db.Column(db.Enum('expense', 'income', name='expense_type'),
                     default='expense')
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

    def set_cost(self):
        self.cost = self.rate * self.quantity

    def __repr__(self):
        return f"Account(id={self.id!r}, type={self.type!r}, category={self.category!r}, " \
               f"operation={self.operation!r}, field={self.field!r}" \
               f"item={self.item!r}, rate={self.rate!r}, quantity={self.quantity!r})"
