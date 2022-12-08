from flask import render_template, redirect, url_for, flash
from flask import request
from . import user_bp
from .forms import LoginForm, SignupForm
from .models import User, UserLog
from flask_login import current_user, login_user
from werkzeug.urls import url_parse
from agriapp import db, flask_bcrypt


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    """login page"""

    # if current_user.is_authenticated:
    #     flash('User {} already logged in'.format(current_user.username),
    #           category='primary')
    #     return redirect(url_for('user.dashboard',
    #                             username=current_user.username))

    form = LoginForm()
    if form.validate_on_submit():
        username = request.form['username']
        password = request.form['password']
        # check_user, user_obj = _check_user_password(username=username,
        #                                             password=password)
        # if check_user:
        #     login_user(user=user_obj)
        #
        #     user_obj.set_last_login()
        #     db.session.add(user_obj)
        #     db.session.commit()
        #
        #     next_page = request.form['next']
        #     if not next_page or url_parse(next_page).netloc != '':
        #         next_page = url_for('user.dashboard', username=username)
        #     flash('You are successfully logged in', category='success')
        #     return redirect(next_page)
        # else:
        #     flash('Wrong username or password', category='error')
        #     return render_template('/login.html', form=form)
    else:
        return render_template('/login.html', form=form)


@user_bp.route('/signup', methods=['GET', 'POST'])
def add_user():
    """add user for app"""
    user_obj = User()
    form = SignupForm(obj=user_obj)

    if form.validate_on_submit():
        # process sign-up information using func into db add info to db here
        # generate user object
        # phone_number = request.form['phone_num-country_code'] + \
        #                request.form['phone_num-phone_num']
        # new_user_obj = User(firstname=request.form['firstname'],
        #                     lastname=request.form['lastname'],
        #                     username=request.form['username'],
        #                     user_type=request.form['type'])
        form.populate_obj(user_obj)

        # add hashed password to db, full name and added_by
        user_obj.set_password(request.form['password'])
        user_obj.set_full_name()

        # check if user with firstname/lastname exists and redirect to enter data again
        if user_obj.is_user_exist():
            flash(message='User {} already exists'.format(user_obj.fullname),
                  category='primary')
            return redirect(url_for('user.add_user'))

        # check if user with username exists and redirect to enter data again
        if user_obj.is_username_exist():
            flash(message='Username {} already exist. '
                          'Provide a different username'.format(user_obj.username),
                  category='primary')
            return redirect(url_for('user.add_user'))

        # add user object to session and commit to db
        db.session.add(user_obj)
        db.session.commit()
        flash('Addition of new user {} successful'.format(request.form['username']),
              category='success')
        return 'User added'
        # return redirect(url_for('user.dashboard', username=current_user.username))

    return render_template('add_user.html', form=form)
