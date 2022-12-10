from agriapp import db


class Fields(db.Model):
    __tablename__ = "fields"

    id = db.Column(db.Integer, primary_key=True)
    geotag = db.Column(db.String(30))
    location = db.Column(db.Enum('tgudi', 'tpuram', name='field_location'),
                         default='tpuram',
                         nullable=False, index=True)
    nickname = db.Column(db.String(10), nullable=False, index=True)
    owner = db.Column(db.String(30))
    survey = db.Column(db.String(10))
    deed = db.Column(db.String(10))


class Equipments(db.Model):
    """all equipments (including water pumps)"""

    __tablename__ = "equipment"

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(10), unique=True, nullable=False, index=True)
    type = db.Column(db.Enum('motorbike', 'pumps', 'sprayer', 'tractor', 'transplanter',
                             name='equipment_type'), default='transplanter',
                     nullable=False)
    geotag = db.Column(db.String(30))
    location = db.Column(db.Enum('tgudi', 'tpuram', 'none', name='field_location'),
                         default='none')
    last_service = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())


class Yield(db.Model):
    __tablename__ = "yield"

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(4), nullable=False, index=True)
    season = db.Column(db.String(10), nullable=False, index=True)
    location = db.Column(db.String(10), db.ForeignKey('fields.location', onupdate='CASCADE',
                                                      ondelete='CASCADE'),
                         nullable=False, index=True)
    variety = db.Column(db.String(10))

    harvest_date = db.Column(db.DateTime.Date(timezone=True))
    sell_date = db.Column(db.DateTime.Date(timezone=True))

    bags = db.Column(db.Integer, nullable=False, default=0)
    bag_weight = db.Column(db.Float)
    bag_rate = db.Column(db.Float)
    buyer = db.Column(db.String(15))

    @db.hybrid_property
    def income(self):
        return self.bags * self.bag_rate

    @db.hybrid_property
    def weight(self):
        """yield in tonnes"""
        return self.bags * self.bag_weight / 1000


class Account(db.Model):
    __tablename__ = "account"

    id = db.Column(db.Integer, primary_key=True)
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
    field = db.Column(db.String(10), db.ForeignKey('fields.location', onupdate='CASCADE',
                                                   ondelete='CASCADE'),
                      index=True)

    @db.hybrid_property
    def cost(self):
        return self.rate * self.quantity



