from agriapp import db


class Fields(db.Model):
    __tablename__ = "fields"

    id = db.Column(db.Integer, primary_key=True)
    geotag = db.Column(db.String(30))
    location = db.Column(db.Enum('tgudi', 'tpuram', name='field_location'), default='tpuram',
                         nullable=False)
    owner = db.Column(db.String(30))
    survey = db.Column(db.String(10))
    deed = db.Column(db.String(10))


class Pumps(db.Model):
    __tablename__ = "pumps"

    id = db.Column(db.Integer, primary_key=True)
    geotag = db.Column(db.String(30))
    location = db.Column(db.Enum('tgudi', 'tpuram', name='field_location'), default='tpuram',
                         nullable=False)
    nickname = db.Column(db.String(10))
    last_service = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())


class Equipments(db.Model):
    __tablename__ = "machines"

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(10))
    type = db.Column(db.Enum('tractor', 'transplanter', 'sprayer', 'motorbike',
                             name='equipment_type'), default='transplanter',
                     nullable=False)
    last_service = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

