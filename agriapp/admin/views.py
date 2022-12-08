from flask import render_template
from . import admin_bp


@admin_bp.route('/')
@admin_bp.route('/home')
def homepage():
    """homepage for agridb"""
    return render_template('index.html')


@admin_bp.route('/faq')
def faq():
    return render_template('faq.html')


@admin_bp.route('/about')
def about():
    return render_template('about.html')


@admin_bp.route('/contact')
def contact_us():
    return render_template('contact_admin.html')
