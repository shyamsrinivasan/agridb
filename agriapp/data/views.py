from flask import render_template, redirect, url_for, flash
from flask import request
from . import data_bp
from .forms import FieldEntry, SelectFieldLocation, LandEntry
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

        flash(message='New field with lands successfully added to database', category='success')
        return redirect(url_for('admin.homepage'))

    return render_template('add_field.html', form=form)


@data_bp.route('/remove/field', methods=['GET', 'POST'])
def remove_field():
    """remove field from db"""
    return render_template('remove_field.html')


@data_bp.route('/add/sowing', methods=['GET', 'POST'])
def add_sowing():
    """add sowing data"""
    return render_template('add_sowing.html')


@data_bp.route('/select/field/<category>', methods=['GET', 'POST'])
def select_field(category):
    """select field location to use for other purposes"""
    form = SelectFieldLocation()

    if form.validate_on_submit():
        location = request.form['location']
        field_obj = db.session.query(Fields).filter(Fields.location == location).first()
        if field_obj is not None:
            if category == 'land':
                flash(message='Add lands to fields in {}'.format(location), category='primary')
                return redirect(url_for('data.add_land', location=location))

        flash(message='No fields with given location. Provide different location', category='error')
        # return render_template('select_field.html', form=form)

    return render_template('select_field.html', form=form)


@data_bp.route('/add/lands/<location>', methods=['GET', 'POST'])
def add_land(location):
    """add land info to go with field info"""

    if location != 'None':
        land_objs = db.session.query(Lands).filter(Lands.field_location == location).all()
        field_obj = db.session.query(Fields).filter(Fields.location == location).first()

        if len(field_obj.field_lands) == 0:
            if land_objs and land_objs is not None:
                field_obj.field_lands = land_objs
            else:
                field_obj.field_lands = [Lands(field_location=location, extent=0.1, owner='nobody',
                                               survey='1/1', deed='1/1')]

        form = LandEntry(obj=field_obj)

        if form.validate_on_submit():

            # check if provided is not altered
            if request.form['field_location'] != field_obj.location:
                form.field_location.data = field_obj.location
            if request.form['field_extent'] != field_obj.field_extent:
                form.field_extent.data = field_obj.field_extent

            form.populate_obj(field_obj)

            for lands in field_obj.field_lands:
                # change location in child relationship object
                if lands.field_location != field_obj.location:
                    lands.field_location = field_obj.location

                # add child object to db session and commit changes
                db.session.add(lands)
                db.session.commit()

            flash(message='New lands successfully added to {} fields'.format(location), category='success')
            return redirect(url_for('admin.homepage'))

        form.field_location.data = field_obj.location
        form.field_extent.data = field_obj.field_extent

        return render_template('add_land.html', form=form, location=location)

    flash(message='Select field location to add lands to', category='primary')
    return redirect(url_for('data.select_field', category='land'))


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



