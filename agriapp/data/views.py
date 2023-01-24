from flask import render_template, redirect, url_for, flash
from flask import request
from datetime import datetime as dt
from datetime import date
import pandas as pd
import numpy as np
from . import data_bp
from .forms import FieldEntry, SelectFieldLocation, LandEntry
from .forms import SowingEntry, RemoveFields, RemoveLand, EquipmentView
from .forms import YieldEntryForm, YieldSowView, EquipmentEntry, AccountEntryForm
from .forms import SeedForm
from .models import Fields, Lands, Sowing, Yields, Equipment, Accounts, AccountEntry
from .models import SeedVariety
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
                         bags=request.form['sow_info-bags'],
                         duration=int(request.form['sow_info-duration']))
        # sow_obj.calculate_harvest(request.form['sow_info-duration'])
        db.session.add(sow_obj)
        db.session.commit()

        flash(message='Sowing data succesfully added', category='success')
        return redirect(url_for('admin.homepage'))

    return render_template('add_sowing.html', form=form)


@data_bp.route('/view/yield-sowing', methods=['GET', 'POST'])
def view_yield_sowing():
    """view sowing data for given season"""

    form = YieldSowView()
    if form.validate_on_submit():
        year = request.form['year']
        season = request.form['season']
        choice = request.form['choice']

        data_func = data_factory(choice)
        data = data_func(season, year)

        if data and data is not None:
            return render_template('view_sowing.html', result=data,
                                   year=year, season=season, choice=choice)
        else:
            flash(message='No {} data available for requested period.'.format(choice),
                  category='primary')

    return render_template('view_sowing.html', form=form)


@data_bp.route('/add/yield/<location>', methods=['GET', 'POST'])
def add_yield(location):
    """add yield data to agri db"""

    field_obj = Fields(location=location)
    if field_obj is None or len(field_obj.yields) == 0:
        field_obj.yields = [Yields(location=location,
                                   harvest_date=date(2022, 12, 22),
                                   sell_date=date(2022, 12, 22),
                                   bags=30, bag_weight=62.0, bag_rate=1200,
                                   buyer='Trader')]

    form = YieldEntryForm(obj=field_obj)
    if form.validate_on_submit():
        # form.populate_obj(field_obj)
        year = request.form['year']
        season = request.form['season']
        for i_input in form.data['yields']:
            input_yields = Yields(location=location, year=year, season=season,
                                  harvest_date=i_input['harvest_date'],
                                  sell_date=i_input['sell_date'],
                                  bags=i_input['bags'], bag_weight=i_input['bag_weight'],
                                  bag_rate=i_input['bag_rate'],
                                  buyer=i_input['buyer'])

            # check if given yield data already exists
            db.session.add(input_yields)
            db.session.commit()

        flash(message='Yield for {}, {} at {} added'.format(season, year, location),
              category='success')
        return redirect(url_for('admin.homepage'))

    return render_template('add_yield.html', form=form, location=location)
    # return render_template('add_yield.html', location=location)


@data_bp.route('/add/machinery', methods=['GET', 'POST'])
def add_equipment():
    """add pump data to agri db"""
    form = EquipmentEntry()
    if form.validate_on_submit():
        nickname = request.form['nickname']
        if request.form['last_service']:
            equip_obj = Equipment(nickname=nickname,
                                  type=request.form['type'],
                                  geotag=request.form['geotag'],
                                  location=request.form['location'],
                                  last_service=dt.strptime(request.form['last_service'], '%Y-%m-%d'))
        else:
            equip_obj = Equipment(nickname=request.form['nickname'],
                                  type=request.form['type'],
                                  geotag=request.form['geotag'],
                                  location=request.form['location'])

        # check if nickname exists
        if equip_obj.check_equipment_nickname():
            flash(message='Equipment Nickname already exists. Change nickname or enter new equipment.',
                  category='error')
            return render_template('add_equipment.html', form=form)

        # if nickname is unique
        db.session.add(equip_obj)
        db.session.commit()

        flash(message='Equipment successfully addedd', category='success')
        return redirect(url_for('admin.homepage'))

    return render_template('add_equipment.html', form=form)


@data_bp.route('/view/machinery/<equipment_type>', methods=['GET', 'POST'])
def view_equipment(equipment_type):
    """view all available equipment"""
    form = EquipmentView()
    if form.validate_on_submit():
        equipment_type = request.form['type']
        data = get_equipment(equipment_type)

        if data and data is not None:
            return render_template('view_equipment.html', result=data, equipment_type=equipment_type)
        else:
            flash(message='No Equipment of type {} in database'.format(equipment_type),
                  category='primary')
            redirect(url_for('data.view_equipment', equipment_type='none'))

    return render_template('view_equipment.html', form=form, equipment_type=equipment_type)


@data_bp.route('/add/seeds', methods=['GET', 'POST'])
def add_seed():
    """add seed varieties from file to db"""
    form = SeedForm()

    if form.validate_on_submit():
        file = request.files['file']
        if file.filename != '':
            # filename = secure_filename(file.filename)
            # upload path
            # uploads = os.path.join(os.path.dirname(appvar.create_app().instance_path),
            #                        'assets', appvar.config.ProdConfig.UPLOAD_FOLDER)
            # save file to path
            # file.save(os.path.join(uploads, filename))

            # prepare df from file
            df = pd.read_excel(file)
            data_df = prepare_data(file)
            seed_obj = SeedVariety(df)

            db.session.add(seed_obj)
            db.session.commit()

            flash(message='New seed varieties added to database')

        return 'Form validated'

    return render_template('add_seed.html', form=form)


@data_bp.route('/add/expense', methods=['GET', 'POST'])
def add_expense():
    """add expense data to agri db"""

    field_obj = db.session.query(Fields).all()
    entry_obj = db.session.query(AccountEntry).first()

    # check if land and field locations are not empty
    if entry_obj is not None and len(entry_obj.account) == 0:
        # dummy land object when no lands are available for field objs
        entry_obj.account = [Accounts(expense_type='expense',
                                      category='labour', operation='field preparation',
                                      rate=0.0, quantity=5)
                             ]
    else:
        entry_obj = AccountEntry()
        entry_obj.account = [Accounts(field='tgudi', expense_type='expense',
                                      category='labour', operation='field preparation',
                                      rate=0.0, quantity=5)
                             ]

    form = AccountEntryForm(obj=entry_obj)
    form.field.choices = [(g.location, g.location) for g in Fields.query.order_by('location')]
    if form.validate_on_submit():
        pass

    return render_template('add_expense.html', form=form)


def check_land_present(land_objs):
    """check if all given land objects are present in db"""

    survey_deed_check = [obj.survey_deed_present() for obj in land_objs]
    # deed_check = [obj.deed_present() for obj in land_objs]
    # survey_deed_check = [obj.survey_deed_present() for obj in land_objs]
    # for obj in land_objs:
    #     survey_present, deed_present = obj.is_present()
    return survey_deed_check


def data_factory(choice):
    if choice == 'yield':
        return get_desired_yield
    elif choice == 'sow':
        return get_desired_sowing


def get_desired_yield(season, year, location=None):
    """get desired yield data from db"""
    if season == 'full_year':
        # search data for all seasons in given year
        yield_data = db.session.query(Yields).filter(Yields.year == year).all()
    elif year == '0000':
        # search data for all years in given season
        yield_data = db.session.query(Yields).filter(Yields.season == season).all()
    elif season == 'all_data':
        # search all yield data
        yield_data = db.session.query(Yields).all()
    else:
        # search data for year and season in db
        yield_data = db.session.query(Yields).filter(Yields.year == year,
                                                     Yields.season == season).all()
    return yield_data


def get_desired_sowing(season, year, location=None):
    """get desired sowing data from db"""
    if season == 'full_year':
        # search data for all seasons in given year
        sow_data = db.session.query(Sowing).filter(Sowing.year == year).all()
    elif year == '0000':
        # search data for all years in given season
        sow_data = db.session.query(Sowing).filter(Sowing.season == season).all()
    elif season == 'all_data':
        # search all sowing data
        sow_data = db.session.query(Sowing).all()
    else:
        # search sowing data for year and season in db
        sow_data = db.session.query(Sowing).filter(Sowing.year == year,
                                                   Sowing.season == season).all()
    return sow_data


def get_equipment(choice):
    """get equipment of specific type"""
    if choice == 'all':
        equip_obj = db.session.query(Equipment).all()
    else:
        equip_obj = db.session.query(Equipment).filter(Equipment.type == choice).all()

    return equip_obj


def prepare_data(file):
    """prepare df for database upload"""

    df = pd.read_excel(file)
    n_rows, _ = df.shape

    d_resistance_exists = [True if x_value['disease_resistance'] is not np.nan else False
                           for _, x_value in df.iterrows()]
    p_resistance_exists = [True if x_value['pest_resistance'] is not np.nan else False
                           for _, x_value in df.iterrows()]
    new_df = pd.concat([df,
                        pd.Series(d_resistance_exists, name='d_resistance_exist'),
                        pd.Series(p_resistance_exists, name='p_resistance_exist')],
                       axis=1)

    changed_names = []
    added_rows = pd.DataFrame(columns=new_df.columns.values)
    for indx, row in new_df.iterrows():
        prepared_df = get_separate_seed_df_rows(row)
        if prepared_df is not None:
            changed_names.append(row['name'])
            added_rows = pd.concat([added_rows, prepared_df], ignore_index=True)

    # drop original row in df
    for i_name in changed_names:
        new_df.drop(new_df[new_df['name'] == i_name].index.values, inplace=True)

    # concatenate df
    new_df = pd.concat([new_df, added_rows], ignore_index=True)
    # drop_df = pd.concat([drop_df, prepared_df], ignore_index=True)
    # added_rows[row['name']] = prepared_df
    # drop_df = new_df.drop(new_df[new_df['name'] == 'ADT47'].index.values)

    return df


def get_separate_seed_df_rows(df):
    """get df w/ separate rows for each disease/pest resistance"""

    disease_resistance = []
    if df['d_resistance_exist']:
        disease_resistance = get_resistance_df(df['disease_resistance'])

    pest_resistance = []
    if df['p_resistance_exist']:
        pest_resistance = get_resistance_df(df['pest_resistance'])

    # new_disease_resistance, new_pest_resistance = [], []
    # if disease_resistance and len(disease_resistance) > 1:
    #     new_df = df[df]
    #     pass

    if pest_resistance and len(pest_resistance) > 1:
        n_pest_resist = len(pest_resistance)
        new_df = df.to_frame().T
        # new_df = info_df.copy(deep=True)
        # new_df = pd.DataFrame(columns=info_df.columns.values)
        new_df = new_df.append([new_df] * (n_pest_resist - 1), ignore_index=True)
        new_df['pest_resistance'] = pest_resistance

        # for indx, value in enumerate(pest_resistance):
        #     new_df

    # if new_disease_resistance or new_pest_resistance:
    #     new_df = pd.Series()
        # for d_resist in disease_resistance:
        #     new_df = pd.Series
        return new_df

    return None


def get_resistance_df(resistance_values):

    if resistance_values is not np.nan:
        resistance_values = resistance_values.split(',')
        new_resistance_values = [i_value.strip() for i_value in resistance_values]
        return new_resistance_values

    return []


