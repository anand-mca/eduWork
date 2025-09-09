
from django.db import connection
from django.shortcuts import redirect, render

from .models import Employer
from django.shortcuts import render, redirect


from django.shortcuts import render, redirect
from django.db import connection

from django.shortcuts import render, redirect
from django.db import connection
from datetime import date
from datetime import datetime

def employer_registration(request):
    if request.method == 'POST':
        o_name = request.POST.get('ownerName')
        shop_name = request.POST.get('shopName')
        category = request.POST.get('category')
        address = request.POST.get('address')

        photo=request.FILES.get('shopLogo')
        photo_path = photo.name if photo else ""

        phone_no = request.POST.get('phone')
        email_id = request.POST.get('email')

        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        map_loc = request.POST.get('locationLink')

        category = request.POST.getlist('category')
        category_str = ", ".join(category)

        if password != confirm_password:
            return render(request, "employer/employer_registration.html", {
                "error": "Passwords do not match!"
            })
        employer = Employer(
            o_name=o_name,
            shop_name=shop_name,
            category=category_str,
            address=address,
            phone_no=phone_no,
            email_id=email_id,
            photo=photo_path,
            map_loc=map_loc
        )
        employer.save()

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO login (username, password, type) VALUES (%s, %s, %s)",
                [email_id, password, "employer"]
            )
        return redirect("employer_registration")

    return render(request, "employer/employer_registration.html")
def employer_profile(request):
    if "username" not in request.session:
        return redirect("login")
    logged_in_email = request.session.get("username")
    try:
        employer = Employer.objects.get(email_id=logged_in_email)
    except Employer.DoesNotExist:
        employer = None
    return render(request, 'employer_profile.html', {'employer': employer})

def emp_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM login WHERE username = %s AND password = %s",
                [username, password]
            )
            user = cursor.fetchone()

        if user:
            request.session['username'] = username
            # Fetch employer details and store in session
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT employer_id, shop_name, address, phone_no, map_loc FROM employer WHERE email_id = %s",
                    [username]
                )
                employer_details = cursor.fetchone()
                if employer_details:
                    request.session['employer_id'] = employer_details[0]
                    request.session['shop_name'] = employer_details[1]
                    request.session['address'] = employer_details[2]
                    request.session['phone_no'] = employer_details[3]
                    request.session['map_loc'] = employer_details[4]
            
            return render(request, "employer/employer_home.html", {
                "message": "Login successful!"
            })
        else:
            return render(request, "employer/login.html", {
                "error": "Invalid credentials!"
            })

    return render(request, "employer/login.html")

def emp_logout_view(request):
    request.session.flush()
    return redirect("employer_login")

def employer_home(request):
    if "username" not in request.session:
        return redirect("login")
    return render(request, "employer/employer_home.html")

def employer_announcement(request):
    if "username" not in request.session:
        return redirect("login")
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        
        with connection.cursor() as cursor:
                current_date = datetime.now().date().strftime("%Y-%m-%d")
                current_time = datetime.now().time().strftime("%H:%M:%S")
                cursor.execute(
                    "INSERT INTO announcement (title, description, date, time) VALUES (%s, %s, %s, %s)",
                    [title, description, current_date, current_time]
                )
        return redirect("employer_announcement")
        # return render(request, "employer/employer_announcement.html", {
        #     "message": "Announcement posted successfully!"
        # })
    return render(request, "employer/employer_announcement.html")

# def post_job(request):
#     if "username" not in request.session:
#         return redirect("login")
#     if request.method == "POST":
#         if "username" not in request.session:
#             return redirect("login")
#         employer_id = request.session.get("employer_id")
#         shop_name = request.session.get("shop_name")
#         address = request.session.get("address")
#         phone_no = request.session.get("phone_no")
#         map_loc = request.session.get("map_loc")
#         job_title = request.POST.get("job_title")
#         job_description = request.POST.get("job_description")
#         job_vacancy = request.POST.get("vacancy")
#         start_date = request.POST.get("start_date")
#         end_date = request.POST.get("end_date")
#         salary = request.POST.get("salary")
#         post_date = datetime.now().date().strftime("%Y-%m-%d")

#         with connection.cursor() as cursor:
#             cursor.execute(
#                 "INSERT INTO job_post (employer_id, post_title, post_description, post_date, shop_name, address, phone_no, vacancy, map_loc, start_date, end_date, salary) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
#                 [employer_id, job_title, job_description, post_date, shop_name, address, phone_no, job_vacancy, map_loc, start_date, end_date, salary]
#             )
#         return redirect("post_job")

#     return render(request, "employer/post_job.html")