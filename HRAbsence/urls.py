from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter
from django.urls import path, include
from .views import *

router = DefaultRouter()
router.register('users', UserView, basename="user")

user_router = NestedDefaultRouter(router, r'users', lookup='user')
user_router.register(r'absences', AbsenceView, basename='absence')

register = DefaultRouter()
register.register('register', RegisterView, basename="register")
business = DefaultRouter()
business.register('business', BusinessView, basename="business")

urlpatterns = [
    path('', include(router.urls)),
    path('', include(register.urls)),
    path('', include(user_router.urls)),
    path('', include(business.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
