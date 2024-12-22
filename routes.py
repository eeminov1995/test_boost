# routes.py

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Users, Profiles
import json

main = Blueprint('main', __name__)

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
        # здесь должна быть проверка корректности введенных данных
        try:
            hash = generate_password_hash(request.form['psw'])
            u = Users(email=request.form['email'], psw=hash)
            db.session.add(u)
            db.session.flush()

            p = Profiles(name=request.form['name'], old=request.form['old'],
                         city=request.form['city'], user_id=u.id)
            db.session.add(p)
            db.session.commit()
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")

        return redirect(url_for('main.index'))

    return render_template("postdata.html", title="postdata")

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

@main.route('/api/purge', methods=['GET'])
def purge_data():
    db.session.query(Users).delete()
    db.session.query(Profiles).delete()
    db.session.commit()
    return render_template('purge.html', title="Очистка данных")
