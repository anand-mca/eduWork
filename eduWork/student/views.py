from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import Student


from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from .models import Student
from django.contrib.auth.hashers import make_password

from django.shortcuts import render, redirect
from django.db import connection
from .models import Student

def student_registration(request):
    if request.method == "POST":
        # Collect data from form
        f_name = request.POST.get("firstName")
        l_name = request.POST.get("lastName")
        dob = request.POST.get("dob")
        age = request.POST.get("age")
        gender = request.POST.get("gender")
        address = request.POST.get("address")
        phone_no = request.POST.get("phone")
        email_id = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirmPassword")

        # Handle skills (checkboxes → comma separated string)
        skills = request.POST.getlist("skills")
        skills_str = ", ".join(skills)

        # Handle profile picture (currently just store file name for now)
        profile_pic = request.FILES.get("profilePicture")
        photo_path = profile_pic.name if profile_pic else ""

        # Validate passwords
        if password != confirm_password:
            return render(request, "student/student_registration.html", {
                "error": "Passwords do not match!"
            })

        # Save student record
        student = Student(
            f_name=f_name,
            l_name=l_name,
            dob=dob,
            age=age,
            gender=gender,
            address=address,
            phone_no=phone_no,
            email_id=email_id,
            skill=skills_str,
            photo=photo_path
        )
        student.save()

        # Save login credentials (email = username)
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO login (username, password) VALUES (%s, %s)",
                [email_id, password]
            )

        return redirect("student_registration")  # reloads form

    return render(request, "student/student_registration.html")




def student_profile(request):
    logged_in_email = "aparna@gmail.com"
    try:
        student = Student.objects.get(email_id=logged_in_email)
    except Student.DoesNotExist:
        student = None
    return render(request, 'student_profile.html', {'student': student})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Query the login table
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM login WHERE username=%s AND password=%s", [username, password])
            row = cursor.fetchone()

        if row:
            # Save session
            request.session["username"] = username
            return redirect("student_home")  # name from urls.py
        else:
            return render(request, "student/login.html", {"error": "Invalid username or password"})

    return render(request, "student/login.html")

def logout_view(request):
    request.session.flush()  # Clear session
    return redirect("login")

def student_home(request):
    # Check if user is logged in
    if "username" not in request.session:
        return redirect("login")  # redirect if not logged in

    return render(request, "student/student_home.html")