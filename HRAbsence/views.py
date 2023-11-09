import datetime

from django.http import HttpResponseRedirect
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from marshmallow import ValidationError
from rest_framework.views import APIView
from HRAbsence.components import *
from HRAbsence.serializers import *
from HRAbsence.models import *

user_ope = UserOpe()
abs_ope = AbsenceOpe()
login_ope = LoginOpe()
business_ope = BusinessOpe()
abs_bus_ope = AbsenceBusinessOpe()
abs_req_ope = AbsenceRequestOpe()

user_ser = UserSerializer()
business_ser = BusinessSerializer()
abs_ser = AbsenceSerializer()
abs_bus_ser = AbsenceBusinessSerializer()
abs_req_ser = AbsenceRequestSerializer()


class LoginView(APIView):
    def post(self, request):
        user = user_ope.usr_by_username(request.data['username'], request.data['password'])
        if user:
            login_info = login_ope.get(request.data['username'])
            login_info.last_login = datetime.datetime.now()
            commit()
            redirect_url = f'/api/user/{user.id}/'
            return HttpResponseRedirect(redirect_url)

        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class UserView(viewsets.ViewSet):
    def list(self, request):
        users = user_ope.list()
        if users:
            result = user_ser.dump(users, many=True)
            return Response(result)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        user = session.get(User, pk)
        if user:
            result = user_ser.dump(user)
            return Response(result)

        return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        try:
            user = user_ser.load(request.data, session=session)
            user_ope.add(user)
            return Response(request.data, status=status.HTTP_201_CREATED)

        except ValidationError as err:
            return Response(err.messages, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'])
    def absence_requests(self, request, pk=None):
        from_ = request.GET.get('from')
        to_ = request.GET.get('to')
        status_ = request.GET.get('status')
        created = request.GET.get('created')
        types = request.GET.getlist('types')
        if from_ is None and to_ is None and status_ is None and created is None and not types:
            absences = abs_ope.get_by_user(pk)
            if absences:
                result = abs_req_ser.dump(absences, many=True)
                return Response(result)

            return Response(status=status.HTTP_404_NOT_FOUND)

        else:
            data = {'from': from_,
                    'to': to_,
                    'status': status_,
                    'created': created,
                    'types': types}
            result = abs_req_ope.get_by_data(data, pk)
            if result:
                ser = AbsenceRequestSerializer(exclude=['absence_id'])
                result = ser.dump(result, many=True)
                return Response(result)
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['GET', 'POST'])
    def employees_requests(self, request, pk=None):
        user = user_ope.get(pk)
        if user and user.role.name == 'Manager':
            requests = abs_req_ope.get_by_business_id(user.business_id)
            if requests:
                if request.method == 'GET':
                    results = abs_req_ser.dump(requests, many=True)
                    return Response(results)
                elif request.method == 'POST':
                    absence_request = request.data
                    updated = []
                    for req in absence_request:
                        absence = abs_req_ope.get(req['id'])
                        updated.append(abs_req_ser.load(req, instance=absence, session=session, partial=True))
                        commit()
                    return Response(abs_req_ser.dump(updated, many=True), status=status.HTTP_207_MULTI_STATUS)

        elif user and user.role.name != 'Manager':
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['GET', 'POST'])
    def request_absence(self, request, pk=None):
        if request.method == 'GET':
            user = user_ope.get(pk)
            absences = abs_ope.get_by_company(user.business_id)
            if absences:
                ser = AbsenceSerializer(exclude=['business'])
                result = ser.dump(absences, many=True)
                return Response(result, status=status.HTTP_200_OK)

            return Response({"message": "Your Company doesn't offer any absence..."})

        elif request.method == 'POST':
            try:
                data, valid, msg = abs_req_ope.handle_request(request.data, pk)

                if not valid:
                    return Response({"message": msg})
                absence = abs_req_ser.load(data, session=session)
                absence.user_id = pk

                abs_req_ope.add(absence)

                return Response(abs_req_ser.dump(absence))

            except ValidationError as err:
                return Response(err.messages, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(viewsets.ViewSet):
    def list(self, request):
        companies = business_ope.list()
        result = business_ser.dump(companies, many=True)
        return Response(result)

    def create(self, request):
        try:
            company = business_ser.load(request.data, session=session)
            business_ope.add(company)
            return Response(request.data, status=status.HTTP_201_CREATED)

        except ValidationError as err:
            return Response(err.messages, status=status.HTTP_400_BAD_REQUEST)


class AbsenceView(viewsets.ViewSet):
    def list(self, request):
        absences = abs_ope.list()
        result = abs_ser.dump(absences, many=True)
        return Response(result)

    def create(self, request):
        try:
            absence = abs_ser.load(request.data, session=session)
            abs_ope.add(absence)
            return Response(request.data, status=status.HTTP_201_CREATED)

        except ValidationError as err:
            return Response(err.messages, status=status.HTTP_400_BAD_REQUEST)


class AbsenceBusinessView(viewsets.ViewSet):
    def list(self, request):
        abs_bus = abs_bus_ope.list()
        result = abs_bus_ser.dump(abs_bus, many=True)
        return Response(result)

    def create(self, request):
        try:
            absence_business = abs_bus_ser.load(request.data, session=session, many=True)
            abs_bus_ope.add(absence_business)
            return Response(request.data, status=status.HTTP_201_CREATED)

        except ValidationError as err:
            return Response(err.messages, status=status.HTTP_400_BAD_REQUEST)


class BusinessView(viewsets.ViewSet):
    def list(self, request):
        companies = business_ope.list()
        result = business_ser.dump(companies, many=True)
        return Response(result)

    def retrieve(self, request, pk=None):
        company = business_ope.get(pk)
        if company:
            result = business_ser.dump(company)
            return Response(result)

        return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        try:
            business = business_ser.load(request.data, session=session)
            business_ope.add(business)
            return Response(request.data, status=status.HTTP_201_CREATED)

        except ValidationError as err:
            return Response(err.messages, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        company = business_ope.get(pk)
        if company:
            try:
                updated = business_ser.load(request.data, instance=company, session=session, partial=True)
                commit()
                return Response(business_ser.dump(updated))

            except ValidationError as err:
                return Response(err.messages, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_404_NOT_FOUND)
