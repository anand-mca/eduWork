
from django.db import connection
from django.shortcuts import redirect, render

from .models import Employer
from django.shortcuts import render, redirect


from django.shortcuts import render, redirect
from django.db import connection

from django.shortcuts import render, redirect
from django.db import connection

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
                "INSERT INTO login (username, password) VALUES (%s, %s)",
                [email_id, password]
            )
        return redirect("employer_registration")

    return render(request, "employer/employer_registration.html")
def employer_profile(request):
    logged_in_email = "sheena@gmail.com"
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
    return redirect("login")

def employer_home(request):
    if "username" not in request.session:
        return redirect("login")
    return render(request, "employer/employer_home.html")
