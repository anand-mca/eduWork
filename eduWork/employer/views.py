
from pyexpat.errors import messages
from django.db import connection
from django.shortcuts import get_object_or_404, redirect, render
from student.models import Jobs

from .models import Employer
from django.shortcuts import render, redirect
from django.contrib import messages


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



def post_job(request):
    if "username" not in request.session:
        return redirect("login")
    if request.method == "POST":
        if "username" not in request.session:
            return redirect("login")
        employer_id = request.session.get("employer_id")
        shop_name = request.session.get("shop_name")
        address = request.session.get("address")
        phone_no = request.session.get("phone_no")
        map_loc = request.session.get("map_loc")
        job_title = request.POST.get("job_title")
        job_description = request.POST.get("job_description")
        job_vacancy = request.POST.get("vacancy")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        salary = request.POST.get("salary")
        post_date = datetime.now().date().strftime("%Y-%m-%d")

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO job_post (employer_id, post_title, post_description, post_date, shop_name, address, phone_no, vacancy, map_loc, start_date, end_date, salary) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                [employer_id, job_title, job_description, post_date, shop_name, address, phone_no, job_vacancy, map_loc, start_date, end_date, salary]
            )
        return redirect("post_job")

    return render(request, "employer/post_job.html")

def view_applications(request):
    if "username" not in request.session:
        return redirect("login")
    
    employer_id = request.session.get("employer_id")
    
    with connection.cursor() as cursor:
        # Get all job posts by this employer with applicant details
        cursor.execute("""
            SELECT jp.job_post_id, jp.post_title, jp.post_description, jp.post_date,
                   jp.shop_name, jp.address, jp.phone_no, jp.vacancy, jp.map_loc,
                   jp.start_date, jp.end_date, jp.salary, jp.student_id
            FROM job_post jp 
            WHERE jp.employer_id = %s
            ORDER BY jp.post_date DESC
        """, [employer_id])
        
        job_data = cursor.fetchall()
        
        # Process the job data to include applicant information
        job_posts = []
        for job in job_data:
            job_dict = {
                'job_post_id': job[0],
                'post_title': job[1],
                'post_description': job[2],
                'post_date': job[3],
                'shop_name': job[4],
                'address': job[5],
                'phone_no': job[6],
                'vacancy': job[7],
                'map_loc': job[8],
                'start_date': job[9],
                'end_date': job[10],
                'salary': job[11],
                'student_id': job[12],
                'applicants': []
            }
            
            # If there are student applications (stored as comma-separated emails)
            if job[12]:  # student_id field contains applicant emails
                applicant_emails = [email.strip() for email in job[12].split(',')]
                
                # Get student details for each applicant
                for email in applicant_emails:
                    cursor.execute("""
                        SELECT student_id, f_name, l_name, email_id, phone_no
                        FROM student 
                        WHERE email_id = %s
                    """, [email])
                    student_data = cursor.fetchone()
                    
                    if student_data:
                        applicant = {
                            'student_id': student_data[0],
                            'student_name': f"{student_data[1]} {student_data[2]}",
                            'student_email': student_data[3],
                            'student_phone': student_data[4],
                            'application_id': f"{job[0]}_{student_data[0]}",  # composite ID
                            'is_accepted': False  # You can implement acceptance logic later
                        }
                        job_dict['applicants'].append(applicant)
            
            job_posts.append(job_dict)
    
    return render(request, "employer/view_applications.html", {"job_posts": job_posts})

def delete_job_post(request, job_post_id):   # <-- match the URLconf
    job = get_object_or_404(Jobs, job_post_id=job_post_id)  # use correct field name

    if request.method == "POST":
        job.delete()
        messages.success(request, "Job post deleted successfully.")
        return redirect("view_applications")

    messages.error(request, "Invalid request.")
    return redirect("view_applications")


