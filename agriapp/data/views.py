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
from .forms import SeedForm, SeedSelectForm, AccountSearchCategoryForm
from .forms import YieldSowIDEntry, SowChangeForm, YieldChangeForm
from .models import Fields, Lands, Sowing, Yields, FieldSowYieldLink
from .models import Equipment, Accounts, AccountEntry, SeedVariety
from .models import EnviromentalData
from .forms import EnvironmentalDataForm
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

            # gather corresponding sow data
            sow_obj = get_desired_sowing(season=season, year=year, location=location)
            input_yields.sow_info.append(sow_obj)
            # check if given yield data already exists
            db.session.add(input_yields)
            db.session.commit()

        flash(message='Yield for {}, {} at {} added'.format(season, year, location),
              category='success')
        return redirect(url_for('admin.homepage'))

    return render_template('add_yield.html', form=form, location=location)
    # return render_template('add_yield.html', location=location)


@data_bp.route('/change-remove/yield-sowing', defaults={'call': 'initial'}, methods=['GET', 'POST'])
@data_bp.route('/change-remove/yield-sowing/<call>', methods=['GET', 'POST'])
def change_yield_sowing(call):
    """change yield/sowing information in db"""

    form = YieldSowView()
    form2 = YieldSowIDEntry()
    if call == 'change':
        if form2.validate_on_submit():
            option = request.form['option']
            desired_id = request.form['desired_id']

            return redirect(url_for('data.review_yield_sow',
                                    option=option, desired_id=desired_id))

    if form.validate_on_submit():
        year = request.form['year']
        season = request.form['season']
        choice = request.form['choice']

        data_func = data_factory(choice)
        data = data_func(season, year)

        if data and data is not None:
            return render_template('change_sowing.html', result=data,
                                   year=year, season=season, choice=choice,
                                   form=form2)
        else:
            flash(message='No {} data available for requested period.'.format(choice),
                  category='primary')

    return render_template('change_sowing.html', form=form)


@data_bp.route('/review/yield-sowing/<option>/<desired_id>', methods=['GET'])
def review_yield_sow(option, desired_id):
    """review yield/sowing information for change removal"""

    result_obj = query_option_fun(option, desired_id)

    if result_obj and result_obj is not None:
        if option == 'sow' and result_obj.__class__.__name__ == 'Sowing':
            form = SowChangeForm(obj=result_obj)
            # sow_info details
            form.sow_info.field_area.data = result_obj.field_area
            form.sow_info.variety.data = result_obj.variety
            form.sow_info.bags.data = result_obj.bags
            form.sow_info.duration.data = result_obj.duration

        elif option == 'yield' and result_obj.__class__.__name__ == 'Yields':
            form = YieldChangeForm(obj=result_obj)
            # yield details
            form.yields.harvest_date.data = result_obj.harvest_date
            form.yields.sell_date.data = result_obj.sell_date
            form.yields.bags.data = result_obj.bags
            form.yields.bag_weight.data = result_obj.bag_weight
            form.yields.bag_rate.data = result_obj.bag_rate
            form.yields.buyer.data = result_obj.buyer

        else:
            form = []

        return render_template('review_sowing.html', option=option,
                               desired_id=desired_id, form=form)

    flash(message='No results for given ID. Check and provide correct ID.',
          category='error')
    return redirect(url_for('data.change_yield_sowing'))


@data_bp.route('/change-remove/yield-sowing/<option>/<desired_id>', methods=['GET', 'POST'])
def change_remove_yield_sow(option, desired_id):
    """change or remove given yield/sow information"""

    if option == 'sow':
        form = SowChangeForm()
    else:   # option == 'yield':
        form = YieldChangeForm()

    if form.validate_on_submit():
        result_obj = query_option_fun(option, desired_id)

        if request.form['option'] == 'change':
            # change only false values
            value_changes = result_obj.compare_change_values(request.form)

            if value_changes:
                db.session.add(result_obj)
                db.session.commit()

                flash(message='Values changed in db for {} id {}'.format(option, desired_id),
                      category='success')
                return redirect(url_for('data.change_yield_sowing'))

            flash(message='No changes provided for {} id {}'.format(option, desired_id),
                  category='primary')
            return redirect(url_for('data.change_yield_sowing'))

        if request.form['option'] == 'remove':
            # remove link between yield and sow tables
            query_obj = remove_option_fun(option, result_obj.id)
            query_obj.delete()
            # remove selected mapped orm object
            db.session.query(result_obj.__class__).\
                filter(result_obj.__class__.id == result_obj.id).delete()
            db.session.commit()

            flash(message='Removed {} id {} from db'.format(option, desired_id),
                  category='success')
            return redirect(url_for('data.change_yield_sowing'))

    flash(message='No changes made', category='primary')
    return redirect(url_for('data.review_yield_sow', option=option, desired_id=desired_id))


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
            data_df = prepare_data(file)
            seed_objs = create_seed_model_obj(data_df)

            varieties_present = True
            for j_seed_obj in seed_objs:
                # check if variety exists in db (only add new varieties)
                seed_present = j_seed_obj.is_present()
                # add obj to session if not present in db
                if not seed_present:
                    varieties_present = False
                    db.session.add(j_seed_obj)
            db.session.commit()

            if not varieties_present:
                flash(message='New seed varieties added to database', category='success')
            else:
                flash(message='Some/All varieties already present in database not added',
                      category='primary')
            return redirect(url_for('admin.homepage'))

        flash(message='No filename given with seed information', category='error')
        return redirect(url_for('data.add_seed'))

    return render_template('add_seed.html', form=form)


@data_bp.route('/view/seed/<grain_type>', defaults={'season': 'all', 'disease_resist': '',
                                                    'pest_resist': ''})
@data_bp.route('/view/seeds/<grain_type>/<season>/<disease_resist>/<pest_resist>')
def view_seeds(grain_type, season='', disease_resist='', pest_resist=''):
    """view different category of seed varities in db"""
    if grain_type != 'none':
        if grain_type != 'all':
            seed_obj = db.session.query(SeedVariety.name).\
                filter(SeedVariety.grain == grain_type)
        else:
            seed_obj = db.session.query(SeedVariety.name)

        if season != 'all':
            seed_obj = seed_obj.filter(SeedVariety.seasons == season)

        if disease_resist and disease_resist != 'none':
            seed_obj = seed_obj.filter(SeedVariety.disease_resistance ==
                                       disease_resist)

        if pest_resist and pest_resist != 'none':
            seed_obj = seed_obj.filter(SeedVariety.pest_resistance ==
                                       pest_resist)

        # collect seeds based on name for display
        grain_obj = seed_obj.all()
        if grain_obj and grain_obj is not None:
            func = arrange_by_seed_name_factory(grain_type)
            arranged_grain_obj = func(grain_obj)
            return render_template('view_seed.html', seeds=arranged_grain_obj,
                                   seed_type=grain_type)

        flash(message='Selected Type/Season/Resistance not available',
              category='error')

    return redirect(url_for('data.select_seed_type'))


@data_bp.route('/view/seeds/select/type', methods=['GET', 'POST'])
def select_seed_type():
    """select type of seed to view"""

    form = SeedSelectForm()
    # get resistance choices from db (set dynamically)
    available_disease_resistance = db.session.query(SeedVariety.disease_resistance).distinct()
    form.disease_resistance.choices = [(i_val[0], i_val[0])
                                       for i_val in available_disease_resistance
                                       if i_val[0]]
    form.disease_resistance.choices.append(('', 'None'))

    available_pest_resistance = db.session.query(SeedVariety.pest_resistance).distinct()
    form.pest_resistance.choices = [(i_val[0], i_val[0])
                                    for i_val in available_pest_resistance
                                    if i_val[0]]
    form.pest_resistance.choices.append(('', 'None'))

    # get season choices dynamically
    available_seasons = db.session.query(SeedVariety.seasons).distinct()
    form.season.choices = [(i_val[0], i_val[0])
                           for i_val in available_seasons
                           if i_val[0]]
    form.season.choices.append(('all', 'All Seasons'))

    if form.validate_on_submit():
        grain_type = request.form['seed_type']
        season = request.form['season']
        pest_resist = 'none'
        if request.form['pest_resistance']:
            pest_resist = request.form['pest_resistance']

        disease_resist = 'none'
        if request.form['disease_resistance']:
            disease_resist = request.form['disease_resistance']

        return redirect(url_for('data.view_seeds', grain_type=grain_type,
                                season=season, pest_resist=pest_resist,
                                disease_resist=disease_resist))

    return render_template('select_seed_type.html', form=form)


@data_bp.route('/add/expense', methods=['GET', 'POST'])
def add_expense():
    """add expense data to agri db"""

    entry_obj = AccountEntry()

    # check if account object is not empty
    if len(entry_obj.account) == 0:
        # dummy land object when no lands are available for field objs
        entry_obj.account = [Accounts(expense_type='expense',
                                      category='labour', operation='field preparation',
                                      rate=0.0, quantity=5)
                             ]

    form = AccountEntryForm(obj=entry_obj)
    form.field.choices = [(g.location, g.location) for g in Fields.query.order_by('location')]
    if form.validate_on_submit():
        # form.populate_obj(entry_obj)
        # get field id
        field_location = form.data['field']
        field_obj = db.session.query(Fields).filter(Fields.location == field_location).first()
        new_entry_obj = AccountEntry(date=form.data['date'], type=form.data['type'],
                                     location_id=field_obj.id)
        account_obj = [Accounts(location_id=field_obj.id,
                                expense_type=new_entry_obj.type,
                                category=i_data['category'],
                                operation=i_data['operation'],
                                item=i_data['item'],
                                rate=i_data['rate'],
                                quantity=i_data['quantity'])
                       for i_data in form.data['account']]

        # add new accounts objs to entry
        new_entry_obj.account = account_obj

        db.session.add(new_entry_obj)
        db.session.commit()

        # x = request.form
        flash(message='Expense successfully added to database', category='success')
        return redirect(url_for('admin.homepage'))

    return render_template('add_expense.html', form=form)


@data_bp.route('/view/expense/<category>', methods=['GET', 'POST'])
def view_expense(category):
    """view expense"""

    if category != 'none':

        return render_template('view_expense.html', category=category)

    return redirect(url_for('data_bp.view_expense_category'))


@data_bp.route('/view/expense/searchby', methods=['GET', 'POST'])
def view_expense_category():
    """choose category to classify expense/income data shown"""
    form = AccountSearchCategoryForm()

    if form.validate_on_submit():
        category = request.form['category']
        return redirect(url_for('data_bp.view_expense', category=category))

    return render_template('view_expense.html', form=form)


@data_bp.route('/add/environmental-data', methods=['GET', 'POST'])
def add_environment_data():
    """add measured data pertaining to temperature, humidity, rainfall, soil pH"""

    form = EnvironmentalDataForm()
    if form.validate_on_submit():
        file = request.files['single_file']
        if file.filename != '':
            # prepare df from file
            # data_df = prepare_data(file)
            # seed_objs = create_seed_model_obj(data_df)

            # add and commit data to db
            # varieties_present = True
            # for j_seed_obj in seed_objs:
            #     # check if variety exists in db (only add new varieties)
            #     seed_present = j_seed_obj.is_present()
            #     # add obj to session if not present in db
            #     if not seed_present:
            #         varieties_present = False
            #         db.session.add(j_seed_obj)
            # db.session.commit()

            # if not varieties_present:
            #     flash(message='New seed varieties added to database', category='success')
            # else:
            #     flash(message='Some/All varieties already present in database not added',
            #           category='primary')
            return redirect(url_for('admin.homepage'))

        flash(message='No filename given', category='error')
        return redirect(url_for('data.add_environment_data'))

    return render_template('add_env_data.html', form=form)


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
    elif choice == 'both':
        return get_yield_and_sow


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

    sow_data = db.session.query(Sowing)
    if location is None:
        if season == 'full_year':
            # search data for all seasons in given year
            sow_data = sow_data.filter(Sowing.year == year).all()
        elif year == '0000':
            # search data for all years in given season
            sow_data = sow_data.filter(Sowing.season == season).all()
        elif season == 'all_data':
            # search all sowing data
            sow_data = sow_data.all()
        else:
            # search sowing data for year and season in db
            sow_data = sow_data.filter(Sowing.year == year,
                                       Sowing.season == season).all()
    else:
        if season == 'full_year':
            # search data for all seasons in given year
            sow_data = sow_data.filter(Sowing.year == year,
                                       Sowing.location == location).all()
        elif year == '0000':
            # search data for all years in given season
            sow_data = sow_data.filter(Sowing.season == season,
                                       Sowing.location == location).all()
        elif season == 'all_data':
            # search all sowing data
            sow_data = sow_data.all()
        else:
            # search sowing data for year and season in db
            sow_data = sow_data.filter(Sowing.year == year,
                                       Sowing.season == season,
                                       Sowing.location == location).first()
    return sow_data


def get_yield_and_sow(season, year, location=None):
    """get both yield and sow data"""

    sow_yield_data = db.session.query(Yields)
    if location is not None:
        sow_yield_data = sow_yield_data.filter(Yields.location == location)

    if season == 'full_year':
        # search data for all seasons in given year
        sow_yield_data = sow_yield_data.filter(Yields.year == year)
    elif year == '0000':
        # search data for all years in given season
        sow_yield_data = sow_yield_data.filter(Yields.season == season)
    # elif season == 'all_data':
    #     # search all sowing data
    #     sow_yield_data = sow_yield_data.all()
    else:
        # search sowing data for year and season in db
        sow_yield_data = sow_yield_data.filter(Yields.year == year,
                                               Yields.season == season)

    sow_yield_data = sow_yield_data.all()
    return sow_yield_data


def get_equipment(choice):
    """get equipment of specific type"""
    if choice == 'all':
        equip_obj = db.session.query(Equipment).all()
    else:
        equip_obj = db.session.query(Equipment).filter(Equipment.type == choice).all()

    return equip_obj


def create_seed_model_obj(data_df):
    """create individual model object for each row in df"""

    seed_objs = [SeedVariety(j_row) for _, j_row in data_df.iterrows()]

    return seed_objs


def prepare_data(file):
    """prepare df for database upload"""

    df = pd.read_excel(file)

    # remove incomplete rows (too many NaNs)
    df = remove_nan_rows(df)
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
    for _, row in new_df.iterrows():
        prepared_df = get_separate_seed_df_rows(row)
        if prepared_df is not None:
            changed_names.append(row['name'])
            added_rows = pd.concat([added_rows, prepared_df], ignore_index=True)

    # change column values to NaN for values with comma separated entries
    added_rows_copy = added_rows.copy(deep=True)
    for indx, row in added_rows.iterrows():
        if row['disease_resistance'] is not np.nan and \
                len(row['disease_resistance'].split(',')) > 1:
            added_rows_copy.iloc[indx]['disease_resistance'] = np.nan
            added_rows_copy.iloc[indx]['d_resistance_exist'] = False

        if row['pest_resistance'] is not np.nan and \
                len(row['pest_resistance'].split(',')) > 1:
            added_rows_copy.iloc[indx]['pest_resistance'] = np.nan
            added_rows_copy.iloc[indx]['p_resistance_exist'] = False

    # drop original row in df (only for modified rows)
    for i_name in changed_names:
        new_df.drop(new_df[new_df['name'] == i_name].index.values, inplace=True)

    # concatenate prepared df to existing df with dropped columns
    new_df = pd.concat([new_df, added_rows_copy], ignore_index=True)

    return new_df


def remove_nan_rows(df):
    """remove rows with too many NaNs - considered as incomplete rows"""

    duration_nan = [ix for ix, val in enumerate(df['duration'].isnull().values) if val]
    season_nan = [ix for ix, val in enumerate(df['average_yield'].isnull().values) if val]
    habit_nan = [ix for ix, val in enumerate(df['habit'].isnull().values) if val]

    full_null_rows = []
    for val in duration_nan:
        if val in season_nan and val in habit_nan:
            full_null_rows.append(val)

    df.drop(full_null_rows, inplace=True)

    # replace empty cells with 0 or none
    df.loc[df['duration'].isnull(), 'duration'] = 0
    df.loc[df['grain_weight'].isnull(), 'grain_weight'] = 0

    return df


def get_separate_seed_df_rows(df):
    """get df w/ separate rows for each disease/pest resistance"""

    disease_resistance = []
    if df['d_resistance_exist']:
        disease_resistance = get_resistance_df(df['disease_resistance'])

    pest_resistance = []
    if df['p_resistance_exist']:
        pest_resistance = get_resistance_df(df['pest_resistance'])

    single_df = df.to_frame().T
    single_disease_df = get_single_resistance_df(original_df=single_df,
                                                 resistance=disease_resistance,
                                                 resistance_type='disease_resistance')
    single_pest_df = get_single_resistance_df(original_df=single_df,
                                              resistance=pest_resistance,
                                              resistance_type='pest_resistance')

    if not single_disease_df.empty and not single_pest_df.empty:
        new_df = pd.concat([single_disease_df, single_pest_df], ignore_index=True)
    elif not single_disease_df.empty:
        new_df = single_disease_df
    elif not single_pest_df.empty:
        new_df = single_pest_df
    else:
        new_df = None

    return new_df


def get_single_resistance_df(original_df: pd.DataFrame, resistance: list, resistance_type: str):
    """get df with resistance having only single value"""

    n_resist = 0
    # single_df = df.to_frame().T
    single_resistance_df = pd.DataFrame(columns=original_df.columns.values)
    if resistance and len(resistance) > 1:
        n_resist = len(resistance)
        single_resistance_df = pd.concat([original_df] * n_resist, ignore_index=True)

    if n_resist > 0:
        single_resistance_df[resistance_type] = resistance

    return single_resistance_df


def get_resistance_df(resistance_values):
    """get resistance values as separate list"""
    if resistance_values is not np.nan:
        resistance_values = resistance_values.split(',')
        new_resistance_values = [i_value.strip() for i_value in resistance_values]
        return new_resistance_values
    return []


def arrange_by_seed_name_factory(grain_type):
    """arrange data as dataframe based on seed names"""

    if grain_type == 'all':
        return arrange_by_seed_name   # arrange_by_seed_name_all
    else:
        return arrange_by_seed_name


def arrange_by_seed_name(seed_names):
    seed_names_set = set(seed_names)
    seed_names = [i_name[0] for i_name in seed_names_set]
    varieties = []

    df_list = [{i_name: pd.read_sql("SELECT * FROM variety WHERE name='{}'".format(i_name),
                                    db.session.connection())} for i_name in seed_names]
    # get of dictionaries
    res = [{key: value.unique() if len(value.unique()) > 1 else value.unique()[0]
            for _, v in i_list.items() for key, value in v.items()}
           for i_list in df_list]
    # convert to df
    result = pd.DataFrame(res)
    result.drop('id', axis=1, inplace=True)
    seed_obj = create_seed_model_obj(result)
    return seed_obj


def query_option_fun(option, desired_id):
    """get db query based on option"""
    result_obj = []
    if option == 'yield':
        # search in yield
        result_obj = db.session.query(Yields).get(desired_id)
    elif option == 'sow':
        # search in row
        result_obj = db.session.query(Sowing).get(desired_id)
    else:
        return None

    return result_obj


def remove_option_fun(option, id):
    """choose option to remove data from correct table in db"""

    if option == 'sow':
        return db.session.query(FieldSowYieldLink).\
            filter(FieldSowYieldLink.sow_id == id)

    elif option == 'yield':
        return db.session.query(FieldSowYieldLink).\
            filter(FieldSowYieldLink.yield_id == id)

    else:
        return None


def prepare_env_data(file_name, sep='\t'):
    """read data from csv file and prepare for db upload"""

    data = pd.read_csv(file_name, sep=sep, header=0)
    # parse df (remove NaN and drop repeated rows
    column_names = data.columns.values.tolist()
    fltr_data = data[data[column_names[0]] != column_names[0]]  # remove rows with data similar to column headers
    fltr_data = fltr_data.dropna()  # get only valid data (NaN and other strings removed)
    return fltr_data