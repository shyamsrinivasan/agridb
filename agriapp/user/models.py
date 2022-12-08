from flask_login import UserMixin
from agriapp import db, flask_bcrypt
from agriapp import login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    fullname = db.Column(db.String(40), nullable=False, index=True)
    type = db.Column(db.Enum('admin', 'user', name='user_type'), default='user')
    username = db.Column(db.String(20), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(60))
    added_on = db.Column(db.DateTime(timezone=True), nullable=False,
                         server_default=db.func.now())

    user_log = db.relationship('UserLog', cascade="all, delete", uselist=False)

    def set_full_name(self):
        """set value of fullname column using first and last name"""
        self.fullname = self.firstname + ' ' + self.lastname

    def set_password(self, password):
        """hash and set password field to hashed value"""
        # hash password using bcrypt
        hashed = flask_bcrypt.generate_password_hash(password=password.encode('utf-8'),
                                                     rounds=12)
        self.password_hash = hashed

    def is_user_exist(self):
        """check if user trying to sign up already exists"""
        user_obj = db.session.query(User).filter(User.firstname == self.firstname,
                                                 User.lastname == self.lastname).first()
        if user_obj is not None:
            return True
        else:
            return False

    def is_username_exist(self):
        """check if user object row already exists in db with given username"""
        user_obj = db.session.query(User).filter(User.username == self.username).first()
        if user_obj is not None:
            return True
        else:
            return False

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.fullname!r}, username={self.username!r}," \
               f"type={self.type!r}, phone={self.phone!r})"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class UserLog(db.Model):
    __tablename__ = 'userlogs'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), db.ForeignKey('users.username', onupdate='CASCADE',
                                                    ondelete='CASCADE'),
                          nullable=False)
    last_login = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    def __repr__(self):
        return f"User(id={self.id!r}, username={self.user_name!r}, " \
               f"LastLogin={self.last_login!r})"

