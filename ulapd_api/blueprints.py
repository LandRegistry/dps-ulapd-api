# Import every blueprint file
from ulapd_api.views import general
from ulapd_api.views.v1 import datasets
from ulapd_api.views.v1 import users
from ulapd_api.views.v1 import activity
from ulapd_api.views.v1 import licence


def register_blueprints(app):
    """Adds all blueprint objects into the app."""
    app.register_blueprint(general.general)
    app.register_blueprint(datasets.datasets, url_prefix='/v1/datasets')
    app.register_blueprint(users.users_bp, url_prefix='/v1/users')
    app.register_blueprint(activity.activity_bp, url_prefix='/v1/activities')
    app.register_blueprint(licence.licence_bp, url_prefix='/v1/licence')

    # All done!
    app.logger.info("Blueprints registered")
