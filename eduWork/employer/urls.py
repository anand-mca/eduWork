from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.employer_profile, name='employer_profile'),
    path('update_employer/', views.update_employer, name='update_employer'),
    path("register/", views.employer_registration, name="employer_registration"),
    path("login/", views.emp_login_view, name="employer_login"),
    path("home/", views.employer_home, name="employer_home"),
    path("logout/", views.emp_logout_view, name="employer_logout"),
    path("announcement/", views.employer_announcement, name="employer_announcement"),
    path("post_job/", views.post_job, name="post_job"),
    path("view_applications/", views.view_applications, name="view_applications"),
    path("delete_job_post/<int:job_post_id>/", views.delete_job_post, name="delete_job_post"),
    path("accept_application/", views.accept_application, name="accept_application"),
    path("view_contract/", views.view_contract, name="view_contract"),
    path("terminate_contract/<int:contract_id>/", views.terminate_contract, name="terminate_contract"),
    path("view_history/", views.view_history, name="view_history"),
    path("view_log/", views.view_log, name="view_log"),
    path("view_rating/", views.view_rating, name="view_rating"),
    path('chat/<str:student_email>/', views.employer_chat, name='employer_chat'),
    path('send-message/', views.employer_send_message, name='employer_send_message'),
    path('post_feedback/', views.post_feedback, name='employer_post_feedback'),
]