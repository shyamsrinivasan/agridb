from flask import render_template, redirect, url_for, flash
from flask import request
from . import data_bp
from .forms import FieldEntry, SelectFieldLocation, LandEntry
from .forms import SowingEntry, RemoveFields, RemoveLand, SowView
from .forms import YieldEntry
from .models import Fields, Lands, Sowing, Yield
from agriapp import db
from datetime import datetime as dt


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


@data_bp.route('/remove/field/<location>/<call_option>', methods=['GET', 'POST'])
def remove_field(location, call_option):
    """remove field from db"""

    form = RemoveFields()
    if call_option == 'display':
        field_obj = db.session.query(Fields).filter(Fields.location == location).first()
        return render_template('remove_field.html', option=call_option, result=field_obj, form=form)

    elif call_option == 'select_field':
        if form.validate_on_submit():
            # get land survey #
            lands = db.session.query(Lands).filter(Lands.field_location == location).all()
            land_survey = [item.survey for item in lands]

            # delete all lands associated with field location
            db.session.query(Lands).filter(Lands.field_location == location).delete()
            db.session.commit()

            # delete all fields at location
            db.session.query(Fields).filter(Fields.location == location).delete()
            db.session.commit()

            flash(message='Field at {} and lands with '
                          'survey # {} deleted'.format(location, land_survey),
                  category='success')
            return redirect(url_for('data.select_field', category='remove_field'))

        flash(message='Field location/land id not provided properly', category='error')
        # return render_template('remove_field.html', option=call_option, location=location, form=form)
        return redirect(url_for('data.remove_field', location=location, call_option='display'))

    flash(message='Invalid call option given. Redirected to home.')
    return redirect(url_for('admin.homepage'))
    # return render_template('remove_field.html', form=form, call_time=call_time)


@data_bp.route('/view/fields')
def view_field():
    """view all available fields and field extents"""

    field_obj = db.session.query(Fields).all()
    if field_obj and field_obj is not None:
        return render_template('view_field.html', result=field_obj)

    flash(message='No fields present in database')
    return redirect(url_for('admin.homepage'))


@data_bp.route('/select/field/<category>', methods=['GET', 'POST'])
def select_field(category):
    """select field location to use for other purposes"""
    form = SelectFieldLocation()

    if form.validate_on_submit():
        location = request.form['location']
        field_obj = db.session.query(Fields).filter(Fields.location == location).first()

        if field_obj is not None:   # if field is present
            if category == 'add_land':
                # add land for existing field
                # flash(message='Add lands to fields in {}'.format(location), category='primary')
                return redirect(url_for('data.add_land', location=location))

            elif category == 'view_land':
                # view all lands in given field location
                return redirect(url_for('data.view_land', location=location))

            elif category == 'remove_land':
                # remove existing land
                flash(message='Remove lands/fields in {}'.format(location), category='primary')
                return redirect(url_for('data.remove_land', location=location, call_option='display'))

            elif category == 'add_yield':
                # add yield data for location
                return redirect(url_for('data.add_yield', location=location))

            elif category == 'remove_field':
                # remove existing land and/or field
                flash(message='Remove lands/fields in {}'.format(location), category='primary')
                return redirect(url_for('data.remove_field', location=location, call_option='display'))

        flash(message='No fields with given location. Provide different location or Add Field',
              category='error')
        return render_template('select_field.html', form=form)

    return render_template('select_field.html', form=form)


@data_bp.route('/add/lands/<location>', methods=['GET', 'POST'])
def add_land(location):
    """add land info to go with field info"""

    # get existing land and field objects for location
    land_objs = db.session.query(Lands).filter(Lands.field_location == location).all()
    field_obj = db.session.query(Fields).filter(Fields.location == location).first()

    # check if land and field locations are not empty
    if len(field_obj.field_lands) == 0:
        # dummy land object when no lands are available for field objs
        field_obj.field_lands = [Lands(field_location=location, extent=0.1, owner='nobody',
                                       survey='1/1', deed='1/1')]
    # new land entry form
    form = LandEntry(obj=field_obj)

    if form.validate_on_submit():
        form.populate_obj(field_obj)

        new_land_objs = [land for land in field_obj.field_lands]
        db.session.close()
        new_field_obj = db.session.query(Fields).filter(Fields.location == location).first()

        land_is_present = check_land_present(new_land_objs)
        n_lands = len(new_land_objs)
        present_lands = [False] * n_lands
        land_added = [True] * n_lands

        for idx, lands in enumerate(new_land_objs):
            # change location in child relationship object
            if lands.field_location != field_obj.location:
                lands.field_location = field_obj.location

            # check if land is present
            if not land_is_present[idx]:
                # add child object to db session and commit changes
                db.session.add(lands)
                db.session.commit()
                land_added[idx] = False
            else:
                present_lands[idx] = True

        if any(present_lands):  # or all(lands_added)
            survey = [new_land_objs[idx].survey for idx, value in enumerate(present_lands) if value]
            flash(message='new lands successfully added to {} fields. '
                          'Survey # {} not added to field database'.format(location, survey),
                  category='primary')
        else:
            flash(message='All new lands successfully added to {} fields'.format(location),
                  category='success')
        return redirect(url_for('admin.homepage'))

    # return redirect(url_for('data.select_field', category='land'))
    return render_template('add_land.html', form=form, location=location, result=land_objs)


@data_bp.route('/remove/land/<location>/<call_option>', methods=['GET', 'POST'])
def remove_land(location, call_option):
    """remove specific land from given field"""

    form = RemoveLand()
    if call_option == 'display':
        field_obj = db.session.query(Fields).filter(Fields.location == location).first()
        return render_template('remove_land.html', option=call_option, result=field_obj, form=form)

    elif call_option == 'select_land':
        if form.validate_on_submit():
            location = request.form['location']
            land_id = request.form['land_id'].split(",")

            land_survey = []
            if land_id:
                # get land survey
                try:
                    land_survey = [db.session.query(Lands).filter(Lands.field_location == location,
                                                                  Lands.id == item).first().survey
                                   for item in land_id]
                except AttributeError:
                    flash(message='Field location/land id not provided properly', category='error')
                    return redirect(url_for('data.select_field', category='remove_field'))

                # delete lands before deleting fields (FK)
                for item in land_id:
                    db.session.query(Lands).filter(Lands.field_location == location,
                                                   Lands.id == item).delete()
                    db.session.commit()

                flash(message='Lands with survey # {} '
                              'at {} deleted'.format(land_survey, location),
                      category='success')
                return redirect(url_for('data.select_field', category='remove_land'))

        flash(message='Field location/land id not provided properly', category='error')
        return redirect(url_for('data.remove_land', location=location, call_option='display'))

    flash(message='Invalid call option given. Redirected to home.')
    return redirect(url_for('admin.homepage'))


@data_bp.route('/view/lands/<location>', methods=['GET', 'POST'])
def view_land(location):
    """view all available lands for given field"""

    field_obj = db.session.query(Fields).filter(Fields.location == location).first()
    if field_obj and field_obj is not None:
        return render_template('view_land.html', location=location, result=field_obj)

    return redirect(url_for('data.select_field', category='view_field'))


@data_bp.route('/view/lands/all')
def view_all_lands():
    """view all lands irrespective of location"""

    # get all locations
    field_location = db.session.query(Fields.location).all()
    # locations = [i_loc[0] for i_loc in field_location]

    # get all lands for each location
    lands = [db.session.query(Lands).filter(Lands.field_location == i_loc[0]).all() for i_loc in field_location]
    land_obj_list = [j_land_obj for i_land in lands for j_land_obj in i_land]
    n_lands = len(land_obj_list)

    return render_template('view_all_land.html', result=land_obj_list, total=n_lands)


@data_bp.route('/add/sowing', methods=['GET', 'POST'])
def add_sowing():
    """add sowing data"""
    sow_obj = Sowing()
    form = SowingEntry(obj=sow_obj)

    if form.validate_on_submit():

        sow_obj = Sowing(year=dt.strptime(request.form['sowing_date'], '%Y-%m-%d').year,
                         season=request.form['season'],
                         location=request.form['location'],
                         sowing_date=dt.strptime(request.form['sowing_date'], '%Y-%m-%d'),
                         field_area=request.form['sow_info-field_area'],
                         variety=request.form['sow_info-variety'],
                         bags=request.form['sow_info-bags'])
        sow_obj.calculate_harvest(request.form['sow_info-duration'])
        db.session.add(sow_obj)
        db.session.commit()

        flash(message='Sowing data succesfully added', category='success')
        return redirect(url_for('admin.homepage'))

    return render_template('add_sowing.html', form=form)


@data_bp.route('/view/sowing', methods=['GET', 'POST'])
def view_sowing():
    """view sowing data for given season"""

    form = SowView()
    if form.validate_on_submit():
        year = request.form['year']
        season = request.form['season']

        # search data for year and season in db
        sow_data = db.session.query(Sowing).filter(Sowing.year == year,
                                                   Sowing.season == season).all()
        if sow_data and sow_data is not None:
            render_template('view_sowing', result=sow_data, year=year, season=season)
        else:
            flash(message='No sowing data available for requested period.', category='primary')

    return render_template('view_sowing.html', form=form)


@data_bp.route('/add/yield/<location>', methods=['GET', 'POST'])
def add_yield(location):
    """add yield data to agri db"""
    form = YieldEntry()
    if form.validate_on_submit():
        pass
        # year, season,
        # harvest_date, sell_date, bags, bag_weight, bag_rate, buyer
    return render_template('add_yield.html', form=form, location=location)


@data_bp.route('/add-pumps', methods=['GET', 'POST'])
def add_pump():
    """add pump data to agri db"""
    return render_template('add_pump.html')


@data_bp.route('/add-expense', methods=['GET', 'POST'])
def add_expense():
    """add expense data to agri db"""
    return render_template('add_expense.html')


def check_land_present(land_objs):
    """check if all given land objects are present in db"""

    survey_deed_check = [obj.survey_deed_present() for obj in land_objs]
    # deed_check = [obj.deed_present() for obj in land_objs]
    # survey_deed_check = [obj.survey_deed_present() for obj in land_objs]
    # for obj in land_objs:
    #     survey_present, deed_present = obj.is_present()
    return survey_deed_check



