from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index),
    path('studentprofile/', views.studentprofile),
    path('announcement/', views.announcement),
    path('contract/', views.contract),
    path('job_history/', views.job_history),
]