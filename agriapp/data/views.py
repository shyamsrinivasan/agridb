from flask import render_template, redirect, url_for, flash
from flask import request
from . import data_bp
from .forms import FieldEntry, SelectFieldLocation, LandEntry
from .forms import SowingEntry
from .models import Fields, Lands, Sowing
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

        if new_obj.is_present():    # check if field is present
            # check if land is present
            survey_deed_check = check_land_present(new_obj.field_lands)
            if all(survey_deed_check):
                flash(message='Field {} and all lands already present. '
                              'Cannot be added'.format(new_obj.location), category='error')
                return redirect(url_for('data.add_field'))

            flash(message='Field {} already present. '
                          'Add lands to fields.'.format(new_obj.location), category='error')
            return redirect(url_for('admin.homepage'))
            # return redirect(url_for('data.add_land', location=new_obj.location))

        db.session.add(new_obj)
        db.session.commit()

        flash(message='New field with lands successfully added to database', category='success')
        return redirect(url_for('admin.homepage'))

    return render_template('add_field.html', form=form)


def check_land_present(land_objs):
    """check if all given land objects are present in db"""

    survey_deed_check = [obj.survey_deed_present() for obj in land_objs]
    # deed_check = [obj.deed_present() for obj in land_objs]
    # survey_deed_check = [obj.survey_deed_present() for obj in land_objs]
    # for obj in land_objs:
    #     survey_present, deed_present = obj.is_present()
    return survey_deed_check


@data_bp.route('/remove/field', methods=['GET', 'POST'])
def remove_field():
    """remove field from db"""
    return render_template('remove_field.html')


@data_bp.route('/add/sowing', methods=['GET', 'POST'])
def add_sowing():
    """add sowing data"""
    sow_obj = Sowing()
    form = SowingEntry(obj=sow_obj)

    if form.validate_on_submit():
        form.populate_obj(sow_obj)

        db.session.add(sow_obj)
        db.session.commit()

        flash(message='Sowing data succesfully added', category='success')
        return redirect(url_for('admin.homepage'))

    return render_template('add_sowing.html', form=form)


@data_bp.route('/select/field/<category>', methods=['GET', 'POST'])
def select_field(category):
    """select field location to use for other purposes"""
    form = SelectFieldLocation()

    if form.validate_on_submit():
        location = request.form['location']
        field_obj = db.session.query(Fields).filter(Fields.location == location).first()

        if field_obj is not None:   # if field is present
            if category == 'land':
                # add land for existing field
                flash(message='Add lands to fields in {}'.format(location), category='primary')
                return redirect(url_for('data.add_land', location=location))

        flash(message='No fields with given location. Provide different location or got to Add Field',
              category='error')
        return render_template('select_field.html', form=form)

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

            # check if provided data is not altered
            if request.form['field_location'] != field_obj.location:
                form.field_location.data = field_obj.location
            if request.form['field_extent'] != field_obj.field_extent:
                form.field_extent.data = field_obj.field_extent

            form.populate_obj(field_obj)

            unadded_lands = []
            for lands in field_obj.field_lands:
                # change location in child relationship object
                if lands.field_location != field_obj.location:
                    lands.field_location = field_obj.location

                # check if land is present
                # if not lands.survey_deed_present():
                    # add child object to db session and commit changes
                    db.session.add(lands)
                    db.session.commit()
                else:
                    unadded_lands.append(lands)

            if unadded_lands:
                unadded_survey = [(unadded_land_obj.survey,
                                   unadded_land_obj.deed)
                                  for unadded_land_obj in unadded_lands]
                flash(message='Lands at {} with survey # {} '
                              'already present'.format(location, unadded_survey),
                      category='error')
                return render_template('add_land.html', form=form, location=location)

            flash(message='New lands successfully added to {} fields'.format(location),
                  category='success')
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



