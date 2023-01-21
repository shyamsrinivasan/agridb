import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = True
    TESTING = False
    CSRF_ENABLED = True

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    DEBUG = True
    SECRET_KEY = os.urandom(32)
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:root@localhost/agridb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    # file upload size max - 4MB
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024


class ProdConfig(Config):
    DEBUG = False
    SECRET_KEY = os.urandom(32)
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:root@localhost/agridb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024


class TestConfig(Config):
    TESTING = True


config = {'development': DevConfig, 'testing': TestConfig, 'default': DevConfig}
