from sqlalchemy.orm import declarative_base, relationship
from HRAbsence.db import engine, get_session
from HRAbsence.enums import *

from sqlalchemy import ForeignKey, Column, String, Integer, DATE, DATETIME, UniqueConstraint, TIMESTAMP, \
    func, Enum

session = get_session()
Base = declarative_base()


class AbsenceBusiness(Base):
    __tablename__ = 'absence_business'

    absence_id = Column(Integer, ForeignKey('absence.id', ondelete='CASCADE'), primary_key=True)
    business_id = Column(Integer, ForeignKey('business.id', ondelete='CASCADE'), primary_key=True)

    def __init__(self, absence_id, business_id):
        self.absence_id = absence_id
        self.business_id = business_id

    def __repr__(self):
        return f"Company ID: {self.business_id}, Absence ID: {self.absence_id} "


class Absence(Base):
    __tablename__ = 'absence'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum(Type), nullable=False)

    def __init__(self, type_):
        self.type = type_

    def __repr__(self):
        return f"{self.type}"


class Business(Base):
    __tablename__ = 'business'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    address = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    phone_number = Column(String(20), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    absences = relationship("Absence", secondary="absence_business", backref='business')

    __table_args__ = (UniqueConstraint("email"),)

    def __init__(self, name, address, email, phone_number):
        self.name = name
        self.address = address
        self.email = email
        self.phone_number = phone_number

    def __repr__(self):
        return f"{self.name}, {self.address}, {self.email}, {self.phone_number}"


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    address = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    role = Column(Enum(Role), nullable=False)
    phone_number = Column(String(20), nullable=False)
    date_of_birth = Column(DATE, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    business_id = Column(Integer, ForeignKey('business.id', ondelete='CASCADE'))

    def __init__(self, first_name, last_name, address, email, role, phone_number, date_of_birth):
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.email = email
        self.role = role
        self.phone_number = phone_number
        self.date_of_birth = date_of_birth

    def __repr__(self):
        return f"det-->[{self.first_name} {self.last_name}, {self.role}, {self.business_id}]"


class Login(Base):
    __tablename__ = 'login'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50))
    password = Column(String(50))
    last_login = Column(DATETIME)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    user_id = Column(Integer, ForeignKey('user.id'))

    __table_args__ = (UniqueConstraint("user_id", "username"),)

    @property
    def is_authenticated(self):
        return True

    def __init__(self, username, password, last_login):
        self.username = username
        self.password = password
        self.last_login = last_login


class AbsenceRequest(Base):
    __tablename__ = 'absence_request'

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(Enum(Status), default="pending")
    start_date = Column(DATE)
    end_date = Column(DATE)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    absence_id = Column(Integer, ForeignKey('absence.id', ondelete='CASCADE'))

    def __init__(self, absence_id, start_date, end_date):
        self.absence_id = absence_id
        self.start_date = start_date
        self.end_date = end_date


Base.metadata.create_all(engine)
