from django.shortcuts import render

# Create your views here.
from .models import Student

def student_profile(request):
    # assuming the logged-in user’s username is same as student.email_id
    logged_in_email = "anand@gmail.com"  
    
    try:
        student = Student.objects.get(email_id=logged_in_email)
    except Student.DoesNotExist:
        student = None

    return render(request, 'student_profile.html', {'student': student})