import os
from flask_script import Manager
from ulapd_api.main import app
from flask_migrate import Migrate, MigrateCommand
from ulapd_api.models import (user_details, user_type, user_terms_link, dataset, activity, licence)  # noqa

from ulapd_api.extensions import db

migrate = Migrate(app, db)

manager = Manager(app)

manager.add_command('db', MigrateCommand)


@manager.command
def runserver(port=9998):
    """Run the app using flask server"""

    os.environ["PYTHONUNBUFFERED"] = "yes"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["COMMIT"] = "LOCAL"

    app.run(debug=True, port=int(port))


if __name__ == "__main__":
    manager.run()
