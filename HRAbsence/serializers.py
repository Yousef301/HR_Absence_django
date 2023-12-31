from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_enum import EnumField
from marshmallow import fields

from .models import *
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
        model = UserAlchemy
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

    parent_lookup_kwargs = {
        'user_pk': 'user__pk',
    }

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
