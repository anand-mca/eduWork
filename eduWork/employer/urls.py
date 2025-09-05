from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.employer_profile, name='employer_profile'),
    path("register/", views.employer_registration, name="employer_registration"),
    path("login/", views.emp_login_view, name="employer_login"),
    path("home/", views.employer_home, name="employer_home"),
    path("logout/", views.emp_logout_view, name="employer_logout"),
]
