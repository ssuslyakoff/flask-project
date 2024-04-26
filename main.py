from flask import Flask, redirect, render_template, session, request, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user
from werkzeug.utils import secure_filename

from db import db_session
from db.user import User
from scripts.forms import LoginForm, RegisterForm

import os
from warnings import filterwarnings
filterwarnings('ignore')

db_session.global_init(os.path.join('db', 'users.db'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

UPLOAD_FOLDER = 'data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def get_user_dir(email):
    return os.path.join(app.config['UPLOAD_FOLDER'], email.replace('@', '').replace('.', ''))


def check_filename(filename):
    return '.' in filename and filename[filename.rfind('.')+1:].lower() in ALLOWED_EXTENSIONS


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    user_email = session.get('user_email', '')
    if user_email != '':
        user_files = os.listdir(get_user_dir(user_email))
        return render_template('storage.html', files=user_files)
    else:
        return render_template('base.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            session['user_email'] = form.email.data
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        # создаем папку для пользователя
        user_dir = get_user_dir(form.email.data)
        if not os.path.exists(user_dir):
            os.mkdir(user_dir)
        # на страницу входа
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session['user_email'] = ''
    return redirect('/')


@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        return redirect('/')
    file = request.files['file']
    if file.filename == '':
        return redirect('/')
    print(check_filename(file.filename))
    if file and check_filename(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(get_user_dir(session.get('user_email')), filename))
        return redirect('/')
    return redirect('/')


@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    filepath = os.path.join(get_user_dir(session.get('user_email')), filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return redirect('/')


@app.route('/rename/<filename>', methods=['POST'])
def rename_file(filename):
    new_filename = request.form['new_filename']
    if new_filename:
        old_filepath = os.path.join(get_user_dir(session.get('user_email')), filename)
        new_filepath = os.path.join(get_user_dir(session.get('user_email')), new_filename)
        os.rename(old_filepath, new_filepath)
    return redirect('/')


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(get_user_dir(session.get('user_email')), filename)


@app.route('/api/download/<email>/<filename>')
def api_download_file(email, filename):
    password = request.json.get('password')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == email).first()
    if user and user.check_password(password):
        return send_from_directory(get_user_dir(email), filename)
    return redirect('/')


@app.route('/api/upload/<email>', methods=['POST'])
def api_upload(email):
    print('!!!')
    if 'file' not in request.files:
        return redirect('/')
    password = request.files['password']
    file = request.files['file']
    if file.filename == '':
        return redirect('/')
    print(file, '!')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == email).first()
    if file and check_filename(file.filename) and user and user.check_password(password):
        filename = secure_filename(file.filename)
        file.save(os.path.join(get_user_dir(email), filename))
        return redirect('/')
    return redirect('/')


@app.route('/api/delete/<email>/<filename>', methods=['POST'])
def api_delete_file(email, filename):
    password = request.json.get('password')
    filepath = os.path.join(get_user_dir(email), filename)
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == email).first()
    if os.path.exists(filepath) and user and user.check_password(password):
        os.remove(filepath)
    return redirect('/')


@app.route('/api/rename/<email>/<filename>/<new_filename>', methods=['POST'])
def api_rename_file(email, filename, new_filename):
    password = request.json.get('password')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == email).first()
    if new_filename and user and user.check_password(password):
        old_filepath = os.path.join(get_user_dir(email), filename)
        new_filepath = os.path.join(get_user_dir(email), new_filename)
        os.rename(old_filepath, new_filepath)
    return redirect('/')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
