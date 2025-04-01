from flask import Flask
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from app.config import Config

ma = Marshmallow()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)   
    app.config.from_object(Config)

    db.init_app(app)
    ma.init_app(app)
    
    with app.app_context():
        from app.routes import main
        app.register_blueprint(main)
        db.create_all() 

    return app
