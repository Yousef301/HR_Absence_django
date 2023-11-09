from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_enum import EnumField
from HRAbsence.models import *
from .enums import *


class BusinessSerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = Business
        sqla_session = session
        include_relationships = True
        load_instance = True
        include_fk = True


class UserSerializer(SQLAlchemyAutoSchema):
    role = EnumField(Role, by_value=False)

    class Meta:
        model = User
        sqla_session = session
        include_relationships = True
        load_instance = True
        include_fk = True


class LoginSerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = Login
        sqla_session = session
        include_relationships = True
        load_instance = True
        include_fk = True


class AbsenceBusinessSerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = AbsenceBusiness
        sqla_session = session
        include_relationships = True
        load_instance = True
        include_fk = True


class AbsenceSerializer(SQLAlchemyAutoSchema):
    type = EnumField(Type, by_value=False)

    class Meta:
        model = Absence
        sqla_session = session
        include_relationships = True
        load_instance = True
        include_fk = True


class AbsenceRequestSerializer(SQLAlchemyAutoSchema):
    status = EnumField(Status, by_value=False)

    class Meta:
        model = AbsenceRequest
        sqla_session = session
        include_relationships = True
        load_instance = True
        # include_fk = True

    user_id = fields.Integer()  # Add a field for the user_id foreign key
    absence_id = fields.Integer()  # Add a field for the absence_id foreign key
