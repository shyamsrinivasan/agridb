from flask import render_template, redirect, url_for, flash
from flask import request
from . import data_bp
from .forms import FieldEntry
from .models import Fields, Lands
from agriapp import db


@data_bp.route('/add/field', methods=['GET', 'POST'])
def add_field():
    """add field data to agri db"""

    # empty field_obj to get first box in html
    field_obj = Fields()
    if field_obj is None or len(field_obj.field_lands) == 0:
        field_obj.field_lands = [Lands(field_location='tgudi', extent=0.1, owner='nobody',
                                       survey='1/1', deed='1/1')]

    form = FieldEntry(obj=field_obj)
    if form.validate_on_submit():
        form.populate_obj(field_obj)
        new_obj = field_obj.fields
        new_obj.field_lands = field_obj.field_lands

        db.session.add(new_obj)
        db.session.commit()

        flash(message='New field successfully added to database', category='success')
        return redirect(url_for('admin.homepage'))

    return render_template('add_field.html', form=form)


@data_bp.route('/remove/field', methods=['GET', 'POST'])
def remove_field():
    """remove field from db"""
    return render_template('remove_field.html')


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



