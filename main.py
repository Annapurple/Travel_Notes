import secrets
from datetime import datetime
from enum import member
from forms.registration_form import RegisterForm
from forms.login_form import LoginForm
from forms.notes_form import NotesForm
from flask import Flask, render_template, redirect, abort, request
from flask_login import login_user, LoginManager, logout_user, login_required, current_user
from data import db_session
from data.notes import Notes
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
db_session.global_init("db/travelers.db")

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def text():
    db_sess = db_session.create_session()
    note = db_sess.query(Notes).filter(Notes.user)
    return render_template("main_page.html", notes=note, title='Notes')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Register form',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Register form',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            email=form.email.data,
            surname=form.surname.data,
            name=form.name.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Register form', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Authorization', form=form)


@app.route('/note', methods=['GET', 'POST'])
@login_required
def add_job():
    form = NotesForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = Notes(
            location=form.location.data,
            information=form.information.data,
            work_size=form.work.data,
            is_anon=form.is_anon.data)
        if job:
            current_user.job.append(job)
            db_sess.merge(job)
            db_sess.commit()
        return redirect('/')
    return render_template('notes_form.html', title='Добавление работы',
                           form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
