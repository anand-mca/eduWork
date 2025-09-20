from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login


from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from .models import Student
from django.contrib.auth.hashers import make_password

from django.shortcuts import render, redirect
from django.db import connection
from .models import Student

from .models import Jobs, Student, Announcement
# Import Contract model from employer app
from employer.models import Contract


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

        # Handle skills (checkboxes â†' comma separated string)
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
                "INSERT INTO login (username, password, type) VALUES (%s, %s, %s)",
                [email_id, password, "student"]
            )

        return redirect("student_registration")  # reloads form

    return render(request, "student/student_registration.html")




def student_profile(request):
    if "username" not in request.session:
        return redirect("login")
    logged_in_email = request.session.get("username")
    try:
        student = Student.objects.get(email_id=logged_in_email)
    except Student.DoesNotExist:
        student = None
    return render(request, 'student/student_profile.html', {'student': student})


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

from .models import Announcement

def student_announcement(request):
    if "username" not in request.session:
        return redirect("login")
    announcements = Announcement.objects.all().order_by('-date', '-time')
    return render(request, "student/student_announcement.html", {"announcements": announcements})



def apply_job(request):
    if "username" not in request.session:
        return redirect("login")

    logged_in_email = request.session.get("username")

    if request.method == "POST":
        job_id = request.POST.get("job_id")  # hidden input from form
        job = get_object_or_404(Jobs, pk=job_id)

        if job.vacancy > 0:
            # Append student email into student_id column
            if job.student_id:  # already has some students
                job.student_id += f", {logged_in_email}"
            else:
                job.student_id = logged_in_email

            # Decrement vacancy
            job.vacancy -= 1
            job.save()
            messages.success(request, "You have successfully applied for this job!")
        else:
            messages.error(request, "Sorry, no vacancies left for this job.")

        return redirect("apply_job")  # reload page after applying

    # GET request â†' show filtered jobs based on student skills
    try:
        # Get current student's skills
        student = Student.objects.get(email_id=logged_in_email)
        student_skills = [skill.strip().lower() for skill in student.skill.split(',')]
        
        # Raw SQL query to get jobs from employers whose category matches student skills
        with connection.cursor() as cursor:
            # Build the SQL query with dynamic LIKE conditions for each skill
            skill_conditions = []
            params = []
            
            for skill in student_skills:
                skill_conditions.append("LOWER(e.category) LIKE %s")
                params.append(f"%{skill}%")
            
            # Join the conditions with OR
            where_clause = " OR ".join(skill_conditions)
            
            query = f"""
                SELECT DISTINCT jp.job_post_id, jp.post_title, jp.post_description, 
                       jp.post_date, jp.shop_name, jp.phone_no, jp.vacancy, 
                       jp.map_loc, jp.start_date, jp.end_date, jp.student_id, jp.salary,
                       jp.employer_id
                FROM job_post jp
                INNER JOIN employer e ON jp.employer_id = e.employer_id
                WHERE ({where_clause}) AND jp.vacancy > 0
                ORDER BY jp.post_date DESC
            """
            
            cursor.execute(query, params)
            job_data = cursor.fetchall()
            
            # Convert to list of dictionaries for easier template usage
            filtered_jobs = []
            for row in job_data:
                job_dict = {
                    'job_post_id': row[0],
                    'post_title': row[1],
                    'post_description': row[2],
                    'post_date': row[3],
                    'shop_name': row[4],
                    'phone_no': row[5],
                    'vacancy': row[6],
                    'map_loc': row[7],
                    'start_date': row[8],
                    'end_date': row[9],
                    'student_id': row[10],
                    'salary': row[11],
                    'employer_id': row[12]
                }
                filtered_jobs.append(job_dict)
        
        return render(request, "student/apply_job.html", {
            "job_post": filtered_jobs,
            "student_skills": student.skill,  # for debugging/display purposes
        })
        
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found. Please complete your registration.")
        return redirect("student_registration")
    except Exception as e:
        # Fallback to show all jobs if there's an error
        messages.warning(request, "Unable to filter jobs by skills. Showing all available jobs.")
        job_post = Jobs.objects.filter(vacancy__gt=0)
        return render(request, "student/apply_job.html", {"job_post": job_post})


def view_contract(request):
    """
    View to display all contracts for the logged-in student
    """
    if "username" not in request.session:
        return redirect("login")
    
    logged_in_email = request.session.get("username")
    
    try:
        # Get the current student's information
        student = Student.objects.get(email_id=logged_in_email)
        student_full_name = f"{student.f_name} {student.l_name}"
        
        # Query contracts for this student using raw SQL to join with job_post table for dates
        with connection.cursor() as cursor:
            query = """
                SELECT c.contract_id, c.post_id, c.student_id, c.employer_id, 
                       c.status, c.salary, c.student_name, c.shop_name,
                       jp.start_date, jp.end_date
                FROM contract c
                LEFT JOIN job_post jp ON c.post_id = jp.job_post_id
                WHERE c.student_id = %s OR c.student_name = %s
                ORDER BY c.contract_id DESC
            """
            cursor.execute(query, [logged_in_email, student_full_name])
            contract_data = cursor.fetchall()
            
            # Convert to list of dictionaries for easier template usage
            contracts = []
            for row in contract_data:
                contract_dict = {
                    'contract_id': row[0],
                    'post_id': row[1],
                    'student_id': row[2],
                    'employer_id': row[3],
                    'status': row[4],
                    'salary': row[5],
                    'student_name': row[6],
                    'shop_name': row[7],
                    'start_date': row[8],
                    'end_date': row[9]
                }
                contracts.append(contract_dict)
        
        return render(request, "student/view_contract.html", {
            "contracts": contracts,
            "student": student
        })
        
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found. Please complete your registration.")
        return redirect("student_registration")
    except Exception as e:
        messages.error(request, f"Error loading contracts: {str(e)}")
        return render(request, "student/view_contract.html", {"contracts": []})