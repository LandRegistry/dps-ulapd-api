from ulapd_api.models.activity import Activity
from ulapd_api.extensions import db
from ulapd_api.utilities.decorators import handle_errors


@handle_errors(is_get=True)
def get_user_activity_list(user_id):
    return _extract_rows(Activity.get_activity_by_user_id(user_id))


@handle_errors(is_get=False)
def add_user_activity(activity_data):
    new_activity = Activity(activity_data)
    db.session.add(new_activity)
    db.session.commit()
    return new_activity.as_dict()


def _extract_rows(rows, map_func=lambda _: _):
    return [map_func(row.as_dict()) for row in rows]
