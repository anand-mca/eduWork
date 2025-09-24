from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.student_profile, name='student_profile'),
    path("register/", views.student_registration, name="student_registration"),
    path("login/", views.login_view, name="login"),
    path("home/", views.student_home, name="student_home"),
    path("logout/", views.logout_view, name="logout"),
    path("announcement/", views.student_announcement, name="student_announcement"),
    path("apply_job/", views.apply_job, name="apply_job"),
    path("view_contract/", views.view_contract, name="student_contract"),
    path("student_history/", views.student_history, name="student_history"),

]





