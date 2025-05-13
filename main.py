import secrets
import requests
from datetime import datetime
from forms.registration_form import RegisterForm
from forms.login_form import LoginForm
from forms.notes_form import NotesForm
from flask import Flask, render_template, redirect, abort, request, url_for, send_file
from flask_login import login_user, LoginManager, logout_user, login_required, current_user
from data import db_session
from data.notes import Notes
from data.users import User
import io

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


@app.route('/user_page')
@login_required
def user_page():
    db_sess = db_session.create_session()
    note = db_sess.query(Notes).filter_by(user=current_user).all()
    return render_template("user_page.html", notes=note, title='Notes')


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
def add_note():
    form = NotesForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        server_address = 'http://geocode-maps.yandex.ru/1.x/?'
        api_key = '8013b162-6b42-4997-9691-77b7074026e0'
        place = form.location.data
        geocoder_request = f'{server_address}apikey={api_key}&geocode={place}&format=json'
        response = requests.get(geocoder_request)
        if response:
            try:
                json_response = response.json()
                toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
                toponym_coodrinates = toponym["Point"]["pos"]
                if int(toponym_coodrinates[0]) > 0 and int(toponym_coodrinates[1]) > 0:
                    location = f'{place} (координаты:{toponym_coodrinates})'
                else:
                    location = place
            except:
                location = place
        else:
            location = place
        color = form.color.data.strip()
        if not (color.startswith('#') and len(color) in [4, 7] and all(
                c in '0123456789abcdefABCDEF' for c in color[1:])):
            color = '#000000'
        else:
            color = form.color.data.strip()
        note = Notes(
            title=form.title.data,
            location=location,
            information=form.information.data,
            image=form.image.data.read(),
            image_name=form.image.data.filename,
            color=color,
            date=datetime.now(),
            is_anon=form.is_anon.data)
        if note:
            current_user.notes.append(note)
            db_sess.merge(note)
            db_sess.commit()
        return redirect('/')
    return render_template('notes_form.html', title='Note adding', form=form)


@app.route('/notes/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_note(id):
    form = NotesForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        notes = db_sess.query(Notes).filter(Notes.id == id,
                                            Notes.user == current_user
                                            ).first()
        if notes:
            form.title.data = notes.title
            form.location.data = notes.location
            form.information.data = notes.information
            form.color.data = notes.color
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        notes = db_sess.query(Notes).filter(Notes.id == id,
                                            Notes.user == current_user
                                            ).first()
        if notes:
            notes.title = form.title.data
            notes.location = form.location.data
            notes.information = form.information.data
            notes.image = form.image.data.read()
            notes.image_name = form.image.data.filename
            notes.is_anon = form.is_anon.data
            notes.color = form.color.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('notes_form.html',
                           title='Note editing',
                           form=form)


def get_content_type(extension):
    if extension == 'png':
        return 'image/png'
    elif extension in ['jpg', 'jpeg']:
        return 'image/jpeg'
    elif extension == 'gif':
        return 'image/gif'
    elif extension == 'mp4':
        return 'video/mp4'
    elif extension == 'avi':
        return 'video/x-msvideo'
    elif extension == 'mov':
        return 'video/quicktime'
    elif extension == 'wmv':
        return 'video/x-ms-wmv'
    return 'application/octet-stream'


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return abort(400, "No file part")
    file = request.files['file']
    if file.filename == '':
        return abort(400, "No selected file")
    file_content = file.read()
    db_sess = db_session.create_session()
    new_note = Notes(image_name=file.filename, image=file_content)
    db_sess.add(new_note)
    db_sess.commit()


@app.route('/images/<filename>', methods=['GET'])
def get_image(filename):
    db_sess = db_session.create_session()
    note = db_sess.query(Notes).filter(Notes.image_name == filename).first()
    if note is None:
        abort(404)
    extension = filename.rsplit('.', 1)[1].lower()
    content_type = get_content_type(extension)
    return send_file(
        io.BytesIO(note.image),
        mimetype=content_type,
        as_attachment=True,
        download_name=filename
    )


@app.route('/notes_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def note_delete(id):
    db_sess = db_session.create_session()
    notes = db_sess.query(Notes).filter(Notes.id == id,
                                        Notes.user == current_user
                                        ).first()
    if notes:
        db_sess.delete(notes)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401


@app.errorhandler(403)
def unauthorized(e):
    return render_template('403.html'), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
