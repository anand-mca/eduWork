from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('home/', views.admin_home, name='admin_home'),
    path('manage-students/', views.manage_students, name='manage_students'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('manage-employers/', views.manage_employers, name='manage_employers'),
    path('delete-employer/<int:employer_id>/', views.delete_employer, name='delete_employer'),
    path('manage-jobs/', views.manage_jobs, name='manage_jobs'),
    path('delete-job/<int:job_id>/', views.delete_job, name='delete_job'),
    path('manage-announcements/', views.manage_announcements, name='manage_announcements'),
    path('delete-announcement/<int:announcement_id>/', views.delete_announcement, name='delete_announcement'),
    path('view-feedbacks/', views.view_feedbacks, name='view_feedbacks'),
]