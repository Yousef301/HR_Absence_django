from sqlalchemy import ForeignKey, Column, String, Integer, DATE, DATETIME, UniqueConstraint, TIMESTAMP, func, Enum, \
    Table
from sqlalchemy.orm import declarative_base, relationship

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.models import Group
from django.db import models

from .db import engine, get_session
from .managers import MyAccountManager
from .enums import *

session = get_session()
Base = declarative_base()


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    user_id = models.IntegerField(verbose_name="user id", unique=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = MyAccountManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class UserAlchemy(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    address = Column(String(50), nullable=False)
    role = Column(Enum(Role), nullable=False)
    phone_number = Column(String(20), nullable=False)
    date_of_birth = Column(DATE, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    password = Column(String(50), nullable=False)
    last_login = Column(DATETIME)

    business_id = Column(Integer, ForeignKey('business.id', ondelete='CASCADE'))

    def __init__(self, first_name, last_name, username, password, business_id, address, email, role, phone_number,
                 date_of_birth):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = password
        self.address = address
        self.email = email
        self.role = role
        self.business_id = business_id
        self.phone_number = phone_number
        self.date_of_birth = date_of_birth

    def __repr__(self):
        return f"det-->[{self.first_name} {self.last_name}, {self.role}, {self.business_id}]"


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


class BusinessGroup(models.Model):
    business_id = models.IntegerField()
    group = models.OneToOneField(Group, on_delete=models.CASCADE)


Base.metadata.create_all(engine)
