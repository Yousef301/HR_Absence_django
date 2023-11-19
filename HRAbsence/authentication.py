from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_

from .models import UserAlchemy, session


class BasicAuthentication(object):
    supports_anonymous_user = True
    supports_inactive_user = True

    def __init__(self):
        self.session = session

    def authenticate(self, username=None, password=None):
        try:
            user = self.session.query(UserAlchemy).filter(
                and_(UserAlchemy.username == username, UserAlchemy.password == password)).first()
            return user
        except NoResultFound:
            return None

    def get_user(self, user_id):
        try:
            user = self.session.query(UserAlchemy).filter_by(id=user_id).one()
        except NoResultFound:
            return None

        return user
