from functools import wraps
from flask import session, redirect, url_for


def login_required(f):
    """
    If 'logged_in' is not in the session redirects to ../login

    Args:
        f (_type_): _description_

    Returns:
        _type_: _description_
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" not in session:
            return redirect("/", code=307)
        return f(*args, **kwargs)

    return decorated_function
