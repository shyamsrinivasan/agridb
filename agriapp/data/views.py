from flask import render_template
from . import data_bp
from agriapp import db


@data_bp.route('/add-field', methods=['GET', 'POST'])
def add_field():
    """add field data to agri db"""
    return render_template('add_field.html')


@data_bp.route('/add-yield', methods=['GET', 'POST'])
def add_yield():
    """add yield data to agri db"""
    return render_template('add_yield.html')


@data_bp.route('/add-pumps', methods=['GET', 'POST'])
def add_pump():
    """add pump data to agri db"""
    return render_template('add_pump.html')


@data_bp.route('/add-expense', methods=['GET', 'POST'])
def add_yield():
    """add expense data to agri db"""
    return render_template('add_expense.html')



