from flask import render_template, redirect, url_for, flash
from flask import request
from . import user_bp
from .forms import LoginForm, SignupForm, ChangePassword
from .models import User, UserLog
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse
from agriapp import db, flask_bcrypt


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    """login page"""

    if current_user.is_authenticated:
        flash('User {} already logged in'.format(current_user.username),
              category='primary')
        return redirect(url_for('admin.homepage'))

    form = LoginForm()
    if form.validate_on_submit():
        username = request.form['username']
        password = request.form['password']
        check_user, user_obj = _check_user_password(username=username,
                                                    password=password)
        if check_user:
            login_user(user=user_obj)

            user_log = UserLog(userid=user_obj.id, username=user_obj.username)
            db.session.add(user_log)
            db.session.commit()

            next_page = request.form['next']
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('admin.homepage')
            flash('You are successfully logged in', category='success')
            return redirect(next_page)
        else:
            flash('Wrong username or password', category='error')
            return render_template('/login.html', form=form)
    else:
        return render_template('/login.html', form=form)


def _check_user_password(username, password):
    """check if password hash in db matches given username and password"""
    user_obj = db.session.query(User).filter(User.username == username).first()
    if user_obj is not None:
        if flask_bcrypt.check_password_hash(user_obj.password_hash, password.encode('utf-8')):
            return True, user_obj
        else:
            return False, None
    else:
        return False, None


@user_bp.route('/logout')
def logout():
    """logout user"""
    if current_user.is_username_exist():
        username = current_user.username
    logout_user()
    flash('User {} logged out succesfully'.format(username),
          category='success')
    return redirect(url_for('admin.homepage'))


@user_bp.route('/signup', methods=['GET', 'POST'])
def add_user():
    """add user for app"""
    user_obj = User()
    form = SignupForm(obj=user_obj)

    if form.validate_on_submit():
        # process sign-up information using func into db add info to db here
        # generate user object
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
        return redirect(url_for('admin.homepage'))
        # return redirect(url_for('user.dashboard', username=current_user.username))

    return render_template('add_user.html', form=form)


@user_bp.route('/<username>/change-password', methods=['GET', 'POST'])
def change_password(username):
    """change password for logged in user"""
    form = ChangePassword()
    if form.validate_on_submit():
        old_password = request.form['old_pass']
        # new_password = request.form['password']
        # check if current password is correct
        check_user, user_obj = _check_user_password(username=current_user.username,
                                                    password=old_password)
        if check_user:
            if not _compare_password(current_user.username,
                                     new_password=request.form['password']):
                user_obj.set_password(request.form['password'])
                # user_obj.set_last_update()

                # add user object to session and commit to db
                db.session.add(user_obj)
                db.session.commit()
                flash('Password changed successfully',
                      category='success')
                return redirect(url_for('admin.homepage'))

            flash('New password cannot be the same as old password.',
                  category='error')
            return render_template('change_password.html', form=form)

        else:
            flash('Wrong password. Enter correct current password to proceed',
                  category='error')
            return redirect(url_for('user.change_password',
                                    username=current_user.username))

    return render_template('change_password.html', form=form)


def _compare_password(username, new_password):
    """compare old and new password hashes"""
    user_obj = db.session.query(User).filter(User.username == username).first()
    if user_obj is not None:
        if flask_bcrypt.check_password_hash(user_obj.password_hash, new_password.encode('utf-8')):
            return True
        else:
            return False
    return False