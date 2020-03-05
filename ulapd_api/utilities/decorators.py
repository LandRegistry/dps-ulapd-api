from ulapd_api.exceptions import ApplicationError
from ulapd_api.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from common_utilities import errors


def handle_errors(is_get):
    def wrapper(func):
        def run_and_handle(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except SQLAlchemyError as e:
                error_code = 500 if is_get else 422
                raise ApplicationError(*errors.get('ulapd_api', 'SQLALCHEMY_ERROR', filler=e), http_code=error_code)
            except ApplicationError as error:
                raise error
            finally:
                if not is_get:
                    db.session.rollback()
                db.session.close()
        return run_and_handle
    return wrapper
