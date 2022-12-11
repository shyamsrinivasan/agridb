from flask import render_template, redirect, url_for, flash
from . import data_bp
from .forms import FieldEntry
from .models import Fields, FieldModel
from agriapp import db


@data_bp.route('/add-field', methods=['GET', 'POST'])
def add_field():
    """add field data to agri db"""

    # empty field_obj to get first box in html
    field_obj = FieldModel()
    # field_obj = Fields(location='tgudi', extent=0.0, nickname='field 1')
    if field_obj is None or len(field_obj.fields) == 0:
        field_obj.fields = [Fields(nickname='field 1')]

    form = FieldEntry(obj=field_obj)
    if form.validate_on_submit():
        flash(message='form validated', category='info')
        return redirect(url_for('admin.homepage'))

    return render_template('add_field.html', form=form)


@data_bp.route('/add-yield', methods=['GET', 'POST'])
def add_yield():
    """add yield data to agri db"""
    return render_template('add_yield.html')


@data_bp.route('/add-pumps', methods=['GET', 'POST'])
def add_pump():
    """add pump data to agri db"""
    return render_template('add_pump.html')


@data_bp.route('/add-expense', methods=['GET', 'POST'])
def add_expense():
    """add expense data to agri db"""
    return render_template('add_expense.html')



