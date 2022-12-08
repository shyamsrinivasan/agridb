from flask import render_template
from . import admin_bp


@admin_bp.route('/')
@admin_bp.route('/index')
def homepage():
    """homepage for agridb"""
    return render_template('index.html')
