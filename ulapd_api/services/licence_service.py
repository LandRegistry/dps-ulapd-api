from ulapd_api.extensions import db
from ulapd_api.models.licence import Licence
from ulapd_api.utilities.decorators import handle_errors


@handle_errors(is_get=False)
def create_licence(data):
    existing_licence = Licence.get_licence_by_licence_name(data['licence_id'])
    if existing_licence:
        db.session.delete(existing_licence)
        db.session.flush()

    new_licence = Licence(data)
    db.session.add(new_licence)
    db.session.commit()
    return new_licence.as_dict()
