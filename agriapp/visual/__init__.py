from flask import Blueprint


visual_bp = Blueprint('visual', __name__, template_folder='templates')
from . import views
