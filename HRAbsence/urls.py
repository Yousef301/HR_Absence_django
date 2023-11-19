from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView, )
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter
from django.urls import path, include
from .views import *

router = DefaultRouter()
router.register(r'businesses', BusinessView, basename="businesses")

businesses_router = NestedDefaultRouter(router, r'businesses', lookup='business')
businesses_router.register(r'users', UserView, basename='users')

user_router = NestedDefaultRouter(businesses_router, r'users', lookup='user')
user_router.register(r'absences', AbsenceView, basename='absences')
#
user_manager_emp = NestedDefaultRouter(businesses_router, r'users', lookup='user')
user_manager_emp.register(r'employees', EmployeesView, basename='employees')

employees_router = NestedDefaultRouter(user_manager_emp, r'employees', lookup='employee')
employees_router.register(r'absences', ManagerView, basename='absences_manager')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(businesses_router.urls)),
    path('', include(user_router.urls)),
    path('', include(user_manager_emp.urls)),
    path('', include(employees_router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
