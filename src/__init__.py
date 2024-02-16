from flask import Flask

from src.config import Config
from src.db import db
from src.scheduler import scheduler
from src.tasks import tasksBlueprint

def create_app(config=Config()) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)

    app.register_blueprint(tasksBlueprint)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    scheduler.init_app(app)

    return app
