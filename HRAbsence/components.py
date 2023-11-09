from datetime import datetime

from sqlalchemy import and_

from HRAbsence.models import *


def commit():
    session.commit()


class AbsenceOpe:
    def get(self, pk=None):
        return session.get(Absence, pk)

    def list(self):
        return session.query(Absence).all()

    def add(self, absence):
        session.add(absence)
        commit()

    def delete(self, absence):
        session.delete(absence)
        commit()

    def get_by_company(self, pk=None):
        return session.query(Absence).join(AbsenceBusiness, Absence.id == AbsenceBusiness.absence_id).filter(
            AbsenceBusiness.business_id == pk).all()

    def get_by_user(self, pk=None):
        return session.query(AbsenceRequest).where(AbsenceRequest.user_id == pk).all()

    def get_by_name(self, names):
        ids = session.query(Absence.id).filter(Absence.type.in_(names)).all()
        return [item[0] for item in ids]


class AbsenceBusinessOpe:
    def get(self, pk=None):
        return session.get(AbsenceBusiness, pk)

    def list(self):
        return session.query(AbsenceBusiness).all()

    def add(self, absence_business):
        session.add(absence_business)
        commit()

    def delete(self, absence_business):
        session.delete(absence_business)
        commit()


class UserOpe:
    def get(self, pk=None):
        return session.get(User, pk)

    def list(self):
        return session.query(User).all()

    def add(self, usr):
        session.add(usr)
        commit()

    def delete(self, usr):
        session.delete(usr)
        commit()

    def usr_by_username(self, username=None, password=None):
        return session.query(User).outerjoin(Login, User.id == Login.user_id).where(
            and_(Login.username == username, Login.password == password)).first()


class BusinessOpe:
    def get(self, pk=None):
        return session.get(Business, pk)

    def list(self):
        return session.query(Business).all()

    def add(self, business):
        session.add(business)
        commit()

    def delete(self, business):
        session.delete(business)
        commit()


class LoginOpe:
    def get(self, username=None):
        return session.query(Login).where(Login.username == username).first()

    def list(self):
        return session.query(Login).all()

    def add(self, login):
        session.add(login)
        commit()

    def delete(self, login):
        session.delete(login)
        commit()


class AbsenceRequestOpe:
    def get(self, pk=None):
        return session.get(AbsenceRequest, pk)

    def list(self):
        return session.query(AbsenceRequest).all()

    def add(self, absence_request):
        session.add(absence_request)
        commit()

    def delete(self, absence_request):
        session.delete(absence_request)
        commit()

    def get_by_business_id(self, pk=None):
        return session.query(AbsenceRequest).join(User, AbsenceRequest.user_id == User.id).filter(
            User.business_id == pk).all()

    def get_by_data(self, data, user_id):
        filters = []
        if data['from'] and data['to']:
            filters.append(AbsenceRequest.start_date.between(data['from'], data['to']))
            filters.append(AbsenceRequest.end_date.between(data['from'], data['to']))
        if data['status']:
            filters.append(AbsenceRequest.status == data['status'])
        if data['created']:
            filters.append(func.cast(AbsenceRequest.created_at, DATE) == data['created'])
        if data['types']:
            abs_ids = AbsenceOpe().get_by_name(data['types'])
            filters.append(AbsenceRequest.absence_id.in_(abs_ids))

        query = session.query(AbsenceRequest).filter(AbsenceRequest.user_id == user_id)
        if filters:
            query = query.filter(and_(*filters))

        return query.all()

    def req_overlap(self, s_d, e_d, user_id):
        abs_requests = session.query(AbsenceRequest).filter(AbsenceRequest.user_id == user_id).all()
        if abs_requests:
            for req in abs_requests:
                start_date = req.start_date
                end_date = req.end_date
                if (s_d <= end_date) and (e_d >= start_date):
                    return False, "Time Overlap..."
        return True, ""

    def handle_request(self, request, pk):
        msg = ""
        abs_id = session.query(Absence.id).filter(Absence.type == request['type']).first()
        user = UserOpe().get(pk)

        valid = False
        if abs_id is not None:
            abs_id = abs_id[0]
        else:
            msg = "Check absence type..."

        available = session.query(AbsenceBusiness).filter(
            and_(AbsenceBusiness.business_id == user.business_id, AbsenceBusiness.absence_id == abs_id)).first()

        if abs_id and available:
            valid = True
        else:
            msg = "The company doesn't offer this type of absence..."

        request['absence_id'] = abs_id

        if valid:
            start_date = datetime.strptime(request['start_date'], "%Y-%m-%d").date()
            end_date = datetime.strptime(request['end_date'], "%Y-%m-%d").date()

            if end_date >= start_date >= datetime.now().date():
                no_overlap, msg = self.req_overlap(start_date, end_date, pk)
                if no_overlap:
                    if request['type'] == 'Vacation' and (start_date - datetime.now().date()).days >= 14:
                        del request['type']
                        return request, valid, msg
                    elif request['type'] in [item.name for item in Type if item.name != 'Vacation']:
                        del request['type']
                        return request, valid, msg
                    msg = "Vacation absence should be requested 14 days before..."
            else:
                msg = "Check the dates you entered..."
            valid = False

        del request['type']
        return request, valid, msg
