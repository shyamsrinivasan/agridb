from flask import render_template, redirect, url_for, flash
from flask import request
from . import user_bp
from flask_login import current_user, login_user
from werkzeug.urls import url_parse
from agriapp import db, flask_bcrypt


@user_bp.route('/login', method=['GET', 'POST'])
def login():
    """login page"""

    if current_user.is_authenticated:
        flash('User {} already logged in'.format(current_user.username),
              category='primary')
        return redirect(url_for('user.dashboard',
                                username=current_user.username))

    form = LoginForm()
    if form.validate_on_submit():
        username = request.form['username']
        password = request.form['password']
        check_user, user_obj = _check_user_password(username=username,
                                                    password=password)
        if check_user:
            login_user(user=user_obj)

            user_obj.set_last_login()
            db.session.add(user_obj)
            db.session.commit()

            next_page = request.form['next']
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('user.dashboard', username=username)
            flash('You are successfully logged in', category='success')
            return redirect(next_page)
        else:
            flash('Wrong username or password', category='error')
            return render_template('/login.html', form=form)
    else:
        return render_template('/login.html', form=form)