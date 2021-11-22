from flask import session
from werkzeug.security import generate_password_hash, check_password_hash

from library.adapters.repository import AbstractRepository
from library.domain.model import User


class NameNotUniqueException(Exception):
    pass


class UnknownUserException(Exception):
    pass


class AuthenticationException(Exception):
    pass


def add_user(user_name: str, password: str, repo: AbstractRepository):
    # Check that the given user name is available.
    user = repo.get_user(user_name)
    if user is not None:
        raise NameNotUniqueException

    # Encrypt password so that the database doesn't store passwords 'in the clear'.
    password_hash = generate_password_hash(password)

    # Create and store the new User, with password encrypted.
    user = User(user_name, password_hash)
    repo.add_user(user)
    repo.add_shelve(user.shelve)


def get_user(user_name: str, repo: AbstractRepository):
    user = repo.get_user(user_name)
    if user is None:
        raise UnknownUserException

    return user_to_dict(user)


def authenticate_user(user_name: str, password: str, repo: AbstractRepository):
    authenticated = False

    user = repo.get_user(user_name)
    if user is not None:
        authenticated = check_password_hash(user.password, password)
    if not authenticated:
        raise AuthenticationException


def user_to_dict(user: User):
    user_dict = {
        'user_name': user.user_name,
        'password': user.password
    }
    return user_dict


def get_user_from_cookie(repo: AbstractRepository) -> User:
    """
    load user entity based on information saved in cookie
    :return: User if found, None otherwise
    """
    if 'user_name' not in session:
        return None
    user_name = session['user_name']
    user = repo.get_user(user_name)
    return user
