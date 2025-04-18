import secrets
from datetime import datetime
from enum import member

from flask import Flask, render_template, redirect, abort, request
from flask_login import login_user, LoginManager, logout_user, login_required, current_user
from data import db_session
from data.notes import Notes
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
db_session.global_init("db/mars_explorer.db")

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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
