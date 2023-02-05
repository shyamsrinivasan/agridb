from flask import Blueprint


analytic_bp = Blueprint('analytics', __name__, template_folder='templates')
from . import methods
