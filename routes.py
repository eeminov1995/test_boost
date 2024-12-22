# routes.py

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Users, Profiles
import json

main = Blueprint('main', __name__)
admin = Blueprint('admin', __name__)

@main.route("/")
def index():
    info = []
    try:
        info = Users.query.all()
    except:
        print("Ошибка чтения из БД")

    return render_template("index.html", title="Главная", list=info)

@main.route("/api/postdata", methods=("POST", "GET"))
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        psw = request.form['psw']
        confirm_psw = request.form['confirm_psw']
        old = request.form['old']
        city = request.form['city']

        if psw != confirm_psw:
            flash("Пароли не совпадают", "error")
            return redirect(url_for('main.register'))

        if int(old) <= 0:
            flash("Возраст должен быть положительным числом", "error")
            return redirect(url_for('main.register'))

        try:
            hash = generate_password_hash(psw)
            u = Users(email=email, psw=hash)
            db.session.add(u)
            db.session.flush()

            p = Profiles(name=name, old=old, city=city, user_id=u.id)
            db.session.add(p)
            db.session.commit()
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")
            flash("Ошибка регистрации", "error")
            return redirect(url_for('main.register'))

        flash("Регистрация успешна", "success")
        return redirect(url_for('main.index'))

    return render_template("postdata.html", title="Регистрация")

@main.route("/login", methods=("POST", "GET"))
def login():
    if request.method == "POST":
        email = request.form['email']
        psw = request.form['psw']

        user = Users.query.filter_by(email=email).first()
        if user and check_password_hash(user.psw, psw):
            session['user_id'] = user.id
            session['role'] = user.role
            flash("Вход выполнен успешно", "success")
            return redirect(url_for('main.index'))
        else:
            flash("Неверный email или пароль", "error")

    return render_template("login.html", title="Вход")

@main.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash("Вы вышли из системы", "success")
    return redirect(url_for('main.index'))

@main.route('/api/getdata', methods=['GET'])
def get_data():
    users = Users.query.all()
    profiles = Profiles.query.all()

    users_data = [
        {
            'id': user.id,
            'email': user.email,
            'psw': user.psw,
            'date': user.date.isoformat() if user.date else None,
            'profile': {
                'id': user.pr.id if user.pr else None,
                'name': user.pr.name if user.pr else None,
                'old': user.pr.old if user.pr else None,
                'city': user.pr.city if user.pr else None
            }
        }
        for user in users
    ]

    profiles_data = [
        {
            'id': profile.id,
            'name': profile.name,
            'old': profile.old,
            'city': profile.city,
            'user_id': profile.user_id
        }
        for profile in profiles
    ]

    response_data = {
        'users': users_data,
        'profiles': profiles_data
    }

    return render_template('getdata.html', title="Данные пользователей и профилей", data=json.dumps(response_data, ensure_ascii=False, indent=4))

@admin.route('/api/purge', methods=['GET'])
def purge_data():
    if 'role' in session and session['role'] == 'admin':
        db.session.query(Users).delete()
        db.session.query(Profiles).delete()
        db.session.commit()
        return render_template('purge.html', title="Очистка данных")
    else:
        flash("Очистить данные может только администратор", "error")
        return redirect(url_for('main.index'))
# routes.py

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Users, Profiles, Posts
import json

main = Blueprint('main', __name__)
admin = Blueprint('admin', __name__)

@main.route("/")
def index():
    posts = Posts.query.all()
    return render_template("index.html", title="Главная", posts=posts)

@main.route("/registration", methods=("POST", "GET"))
def registration():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        psw = request.form['psw']
        confirm_psw = request.form['confirm_psw']
        old = request.form['old']
        city = request.form['city']

        if psw != confirm_psw:
            flash("Пароли не совпадают", "error")
            return redirect(url_for('main.registration'))

        if int(old) <= 0:
            flash("Возраст должен быть положительным числом", "error")
            return redirect(url_for('main.registration'))

        try:
            hash = generate_password_hash(psw)
            role = 'admin' if email == 'e.eminov1995@mail.ru' and psw == 'admin' else 'user'
            u = Users(email=email, psw=hash, role=role)
            db.session.add(u)
            db.session.flush()

            p = Profiles(name=name, old=old, city=city, user_id=u.id)
            db.session.add(p)
            db.session.commit()
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")
            flash("Ошибка регистрации", "error")
            return redirect(url_for('main.registration'))

        flash("Регистрация успешна", "success")
        return redirect(url_for('main.index'))

    return render_template("postdata.html", title="Регистрация")

@main.route("/login", methods=("POST", "GET"))
def login():
    if request.method == "POST":
        email = request.form['email']
        psw = request.form['psw']

        user = Users.query.filter_by(email=email).first()
        if user and check_password_hash(user.psw, psw):
            session['user_id'] = user.id
            session['role'] = user.role
            flash("Вход выполнен успешно", "success")
            return redirect(url_for('main.index'))
        else:
            flash("Неверный email или пароль", "error")

    return render_template("login.html", title="Вход")

@main.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash("Вы вышли из системы", "success")
    return redirect(url_for('main.index'))

@main.route("/api/postdata", methods=("POST", "GET"))
def create_post():
    if 'user_id' not in session:
        flash("Вы должны быть авторизованы, чтобы создать пост", "error")
        return redirect(url_for('main.login'))

    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']

        try:
            post = Posts(title=title, content=content, user_id=session['user_id'])
            db.session.add(post)
            db.session.commit()
        except:
            db.session.rollback()
            print("Ошибка добавления поста в БД")
            flash("Ошибка создания поста", "error")
            return redirect(url_for('main.create_post'))

        flash("Пост создан успешно", "success")
        return redirect(url_for('main.index'))

    return render_template("create_post.html", title="Создать пост")

@main.route("/api/delete_post/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    post = Posts.query.get_or_404(post_id)
    if 'user_id' not in session:
        flash("Вы должны быть авторизованы, чтобы удалить пост", "error")
        return redirect(url_for('main.login'))

    if session['user_id'] == post.user_id or session['role'] == 'admin':
        try:
            db.session.delete(post)
            db.session.commit()
            flash("Пост удален успешно", "success")
        except:
            db.session.rollback()
            print("Ошибка удаления поста из БД")
            flash("Ошибка удаления поста", "error")
    else:
        flash("Вы не можете удалить этот пост", "error")

    return redirect(url_for('main.index'))

@main.route('/api/getdata', methods=['GET'])
def get_data():
    users = Users.query.all()
    profiles = Profiles.query.all()

    users_data = [
        {
            'id': user.id,
            'email': user.email,
            'psw': user.psw,
            'date': user.date.isoformat() if user.date else None,
            'profile': {
                'id': user.pr.id if user.pr else None,
                'name': user.pr.name if user.pr else None,
                'old': user.pr.old if user.pr else None,
                'city': user.pr.city if user.pr else None
            }
        }
        for user in users
    ]

    profiles_data = [
        {
            'id': profile.id,
            'name': profile.name,
            'old': profile.old,
            'city': profile.city,
            'user_id': profile.user_id
        }
        for profile in profiles
    ]

    response_data = {
        'users': users_data,
        'profiles': profiles_data
    }

    return render_template('getdata.html', title="Данные пользователей и профилей", data=json.dumps(response_data, ensure_ascii=False, indent=4))

@admin.route('/api/purge', methods=['GET'])
def purge_data():
    if 'role' in session and session['role'] == 'admin':
        db.session.query(Users).delete()
        db.session.query(Profiles).delete()
        db.session.query(Posts).delete()
        db.session.commit()
        return render_template('purge.html', title="Очистка данных")
    else:
        flash("Очистить данные может только администратор", "error")
        return redirect(url_for('main.index'))
