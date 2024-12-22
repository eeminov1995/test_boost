# __init__.py

from flask import Flask
from config import Config
from models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = 'supersecretkey'  # Добавим секретный ключ для сессий

    db.init_app(app)

    with app.app_context():
        db.create_all()

    from routes import main, admin
    app.register_blueprint(main)
    app.register_blueprint(admin, url_prefix='/admin')

    return app
