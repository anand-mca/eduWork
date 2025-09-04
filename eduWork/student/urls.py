from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.student_profile, name='student_profile'),
    path("register/", views.student_registration, name="student_registration"),
    path("login/", views.login_view, name="login"),
    path("home/", views.student_home, name="student_home"),
    path("logout/", views.logout_view, name="logout"),
]




