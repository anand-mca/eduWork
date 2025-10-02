from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.student_profile, name='student_profile'),
    path('update_student/', views.update_student, name="update_student"),
    path("register/", views.student_registration, name="student_registration"),
    path("login/", views.login_view, name="login"),
    path("home/", views.student_home, name="student_home"),
    path("logout/", views.logout_view, name="logout"),
    path("announcement/", views.student_announcement, name="student_announcement"),
    path("apply_job/", views.apply_job, name="apply_job"),
    path("view_contract/", views.view_contract, name="student_contract"),
    path("student_history/", views.student_history, name="student_history"),
    path("rate_workspace/", views.rate_workspace, name="rate_workspace"),
    path('chat/<str:employer_email>/', views.student_chat, name='student_chat'),
    path('send_message/', views.send_message, name='send_message'),
    path('schedule_studies/', views.schedule_studies, name='schedule_studies'),
    path('delete_schedule/<int:academic_id>/', views.delete_schedule, name='delete_schedule'),
    path('post_feedback/', views.post_feedback, name='post_feedback'),
]





