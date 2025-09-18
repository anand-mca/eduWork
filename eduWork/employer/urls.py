from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.employer_profile, name='employer_profile'),
    path("register/", views.employer_registration, name="employer_registration"),
    path("login/", views.emp_login_view, name="employer_login"),
    path("home/", views.employer_home, name="employer_home"),
    path("logout/", views.emp_logout_view, name="employer_logout"),
    path("announcement/", views.employer_announcement, name="employer_announcement"),
    path("post_job/", views.post_job, name="post_job"),
    path("view_applications/", views.view_applications, name="view_applications"),
    path("delete_job_post/<int:job_post_id>/", views.delete_job_post, name="delete_job_post"),

    ]
