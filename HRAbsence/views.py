from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.views import APIView

from django.contrib.auth import authenticate
from marshmallow import ValidationError

from .permissions import ManagerPermissions
from .serializers import *
from .components import *
from .models import *

user_ope = UserOpe()
abs_ope = AbsenceOpe()
business_ope = BusinessOpe()
abs_req_ope = AbsenceRequestOpe()
abs_bus_ope = AbsenceBusinessOpe()

user_ser = UserSerializer()
abs_ser = AbsenceSerializer()
business_ser = BusinessSerializer()
abs_req_ser = AbsenceRequestSerializer()
abs_bus_ser = AbsenceBusinessSerializer()


class LoginView(APIView):

    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        user = authenticate(username=username, password=password)
        refresh = RefreshToken.for_user(user)

        return Response({'refresh': str(refresh),
                         'access': str(refresh.access_token)})


class RegisterView(APIView):
    def post(self, request):
        try:
            user = user_ser.load(request.data, session=session)
            user_ope.add(user)

            # Add user to auth table
            usr = User.objects.create_user(username=user.username, email=user.email, user_id=user.id)
            usr.set_password(user.password)
            usr.user_id = user.id
            usr.is_staff = True
            usr._role = user.role.name
            usr._business = user.business_id

            usr.save()

            commit()
            return Response(request.data, status=status.HTTP_201_CREATED)

        except ValidationError as err:
            return Response(err.messages, status=status.HTTP_400_BAD_REQUEST)


class UserView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, business_pk=None):
        users = user_ope.list(business_pk)
        if users:
            result = user_ser.dump(users, many=True)
            return Response(result)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None, business_pk=None):
        req = user_ope.get(pk, business_pk)
        if req:
            result = user_ser.dump(req)
            return Response(result)

        return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        try:
            user = user_ser.load(request.data, session=session)
            user_ope.add(user)
            return Response(request.data, status=status.HTTP_201_CREATED)

        except ValidationError as err:
            return Response(err.messages, status=status.HTTP_400_BAD_REQUEST)


class AbsenceView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, business_pk=None, user_pk=None):
        from_ = request.GET.get('from')
        to_ = request.GET.get('to')
        status_ = request.GET.get('status')
        created = request.GET.get('created')
        types = request.GET.getlist('types')
        if from_ is None and to_ is None and status_ is None and created is None and not types:
            absences = abs_ope.get_by_user(user_pk, business_pk)
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
            result = abs_req_ope.get_by_data(data, request.user.user_id)
            if result:
                ser = AbsenceRequestSerializer(exclude=['absence_id'])
                result = ser.dump(result, many=True)
                return Response(result)
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request, user_pk=None):
        try:
            data, valid, msg = abs_req_ope.handle_request(request.data, user_pk)

            if not valid:
                return Response({"message": msg})
            absence = abs_req_ser.load(data, session=session)
            absence.user_id = user_pk

            abs_req_ope.add(absence)

            return Response(abs_req_ser.dump(absence))

        except ValidationError as err:
            return Response(err.messages, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None, business_pk=None, user_pk=None):
        req = abs_req_ope.get(pk)
        if req:
            result = abs_req_ser.dump(req)
            return Response(result)

        return Response(status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, pk=None):
        absence = abs_req_ope.get(pk)
        if absence:
            try:
                if request.data['status'] and (request.data['status'] != absence.status):
                    return Response({"Message: ": "You don't have the permission to approve the request..."})
                updated = business_ser.load(request.data, instance=absence, session=session, partial=True)
                commit()
                return Response(business_ser.dump(updated))

            except ValidationError as err:
                return Response(err.messages, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_404_NOT_FOUND)


class BusinessView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        companies = business_ope.list()
        if companies:
            result = business_ser.dump(companies, many=True)
            return Response(result)

        return Response(status=status.HTTP_404_NOT_FOUND)

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


class EmployeesView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ManagerPermissions]

    def list(self, request, user_pk=None, business_pk=None):
        manager = user_ope.get(user_pk, business_pk)
        users = user_ope.users_by_manager_id(manager)
        if users:
            results = user_ser.dump(users, many=True)
            return Response(results)

        return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None, business_pk=None, user_pk=None):
        user = user_ope.get(pk, business_pk)
        if user:
            result = user_ser.dump(user)
            return Response(result)

        return Response(status=status.HTTP_404_NOT_FOUND)


class ManagerView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ManagerPermissions]

    def list(self, request, user_pk=None, business_pk=None, employee_pk=None):
        manager = user_ope.get(user_pk, business_pk)
        requests = abs_req_ope.get_by_business_id(manager.business_id)
        if requests:
            results = abs_req_ser.dump(requests, many=True)
            return Response(results)

        return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None, user_pk=None, business_pk=None, employee_pk=None):
        absence = abs_req_ope.get(pk)
        if absence:
            result = abs_req_ser.dump(absence)
            return Response(result)

        return Response(status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, pk=None, user_pk=None, business_pk=None, employee_pk=None):
        absence = abs_req_ope.get(pk)
        if absence:
            try:
                updated = abs_req_ser.load(request.data, instance=absence, session=session, partial=True)
                commit()
                return Response(abs_req_ser.dump(updated))

            except ValidationError as err:
                return Response(err.messages, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_404_NOT_FOUND)
