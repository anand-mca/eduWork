
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login

from django.utils import timezone

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

        # Check if student has already applied for this job
        if job.student_id:
            # Convert comma-separated emails to list for checking
            applied_emails = [email.strip() for email in job.student_id.split(',')]
            if logged_in_email in applied_emails:
                messages.warning(request, "You have already applied for this job.")
                return redirect("apply_job")

        # Check if vacancy is available
        if job.vacancy > 0:
            # Add student email to applicants list
            if job.student_id:  # already has some students
                job.student_id += f", {logged_in_email}"
            else:
                job.student_id = logged_in_email

            # Save the job (vacancy decrement removed - will be done when employer accepts)
            job.save()
            messages.success(request, "You have successfully applied for this job!")
        else:
            messages.error(request, "Sorry, no vacancies left for this job.")

        return redirect("apply_job")  # reload page after applying

    # GET request - show filtered jobs based on student skills
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
                # Check if current student has already applied
                student_emails = row[10].split(',') if row[10] else []
                student_emails = [email.strip() for email in student_emails]
                has_applied = logged_in_email in student_emails
                
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
                    'employer_id': row[12],
                    'has_applied': has_applied  # New field to track if student already applied
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
        
        # Add has_applied field for fallback jobs too
        for job in job_post:
            student_emails = job.student_id.split(',') if job.student_id else []
            student_emails = [email.strip() for email in student_emails]
            job.has_applied = logged_in_email in student_emails
        
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
    
def student_history(request):
    """
    View to display comprehensive job history for the logged-in student with statistics
    """
    if "username" not in request.session:
        return redirect("login")
    
    logged_in_email = request.session.get("username")
    
    try:
        # Get the current student's information
        student = Student.objects.get(email_id=logged_in_email)
        
        with connection.cursor() as cursor:
            # Get comprehensive job history for this student with job details
            cursor.execute("""
                SELECT jh.log_id, jh.contract_id, jh.student_id, jh.employer_id,
                       jh.join_date, jh.leaving_date, jh.total_salary,
                       jp.post_title, jp.shop_name, e.shop_name as employer_shop_name,
                       e.o_name as employer_owner_name
                FROM job_history jh
                LEFT JOIN contract c ON jh.contract_id = c.contract_id
                LEFT JOIN job_post jp ON c.post_id = jp.job_post_id
                LEFT JOIN employer e ON jh.employer_id = e.email_id
                WHERE jh.student_id = %s
                ORDER BY jh.leaving_date DESC, jh.join_date DESC
            """, [logged_in_email])
            
            history_data = cursor.fetchall()
            
            # Convert to list of dictionaries and calculate statistics
            job_history = []
            total_jobs = len(history_data)
            total_experience_days = 0
            total_earnings = 0
            
            for row in history_data:
                # Calculate working days
                join_date = row[4]
                leaving_date = row[5]
                if join_date and leaving_date:
                    working_days = (leaving_date - join_date).days + 1
                    total_experience_days += working_days
                else:
                    working_days = 0
                
                # Add to total earnings
                try:
                    salary = int(row[6]) if row[6] else 0
                    total_earnings += salary
                except (ValueError, TypeError):
                    salary = 0
                
                history_dict = {
                    'log_id': row[0],
                    'contract_id': row[1],
                    'student_id': row[2],
                    'employer_id': row[3],
                    'join_date': row[4],
                    'leaving_date': row[5],
                    'total_salary': row[6],
                    'job_title': row[7] if row[7] else 'N/A',
                    'shop_name': row[8] if row[8] else (row[9] if row[9] else 'N/A'),
                    'employer_name': row[10] if row[10] else 'N/A',
                    'working_days': working_days,
                    'daily_rate': salary // working_days if working_days > 0 else 0,
                    'end_date': row[5]  # For template compatibility
                }
                job_history.append(history_dict)
            
            # Calculate comprehensive summary statistics
            experience_summary = {
                'total_jobs': total_jobs,
                'total_experience_days': total_experience_days,
                'total_earnings': total_earnings,
                'average_job_duration': total_experience_days // total_jobs if total_jobs > 0 else 0,
                'average_daily_rate': total_earnings // total_experience_days if total_experience_days > 0 else 0,
                'experience_months': round(total_experience_days / 30.44, 1) if total_experience_days > 0 else 0  # Convert to months
            }
            
            # Prepare student info for display
            student_info = {
                'name': f"{student.f_name} {student.l_name}",
                'email': student.email_id,
                'phone': student.phone_no,
                'skills': student.skill,
                'age': student.age,
                'address': student.address
            }
        
        return render(request, "student/student_history.html", {
            "student_info": student_info,
            "job_history": job_history,
            "experience_summary": experience_summary,
            "student": student
        })
        
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found. Please complete your registration.")
        return redirect("student_registration")
    except Exception as e:
        messages.error(request, f"Error loading job history: {str(e)}")
        return render(request, "student/student_history.html", {
            "job_history": [],
            "experience_summary": {
                'total_jobs': 0,
                'total_experience_days': 0,
                'total_earnings': 0,
                'average_job_duration': 0,
                'average_daily_rate': 0,
                'experience_months': 0
            }
        })
def rate_workspace(request):
    """
    View to handle workspace rating functionality
    """
    if "username" not in request.session:
        return redirect("login")
    
    logged_in_email = request.session.get("username")
    
    # Get contract_id and employer_id from URL parameters if provided
    contract_id = request.GET.get('contract_id')
    employer_id = request.GET.get('employer_id')
    
    if request.method == "POST":
        # Get form data
        rating = request.POST.get("rating")
        description = request.POST.get("description", "")
        contract_id = request.POST.get("contract_id", "")
        employer_id = request.POST.get("employer_id", "")
        
        # Validate rating
        if not rating or not rating.isdigit() or int(rating) < 1 or int(rating) > 5:
            messages.error(request, "Please select a valid rating (1-5 stars).")
            return render(request, "student/rating.html", {
                'contract_id': contract_id,
                'employer_id': employer_id
            })
        
        try:
            # Get student information
            student = Student.objects.get(email_id=logged_in_email)
            student_full_name = f"{student.f_name} {student.l_name}"
            
            # Insert rating into database
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO rating (student_id, employer_id, contract_id, star, description, date_time)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, [
                    logged_in_email,
                    employer_id,
                    contract_id,
                    int(rating),
                    description,
                    timezone.now()
                ])
            
            messages.success(request, "Thank you! Your rating has been submitted successfully.")
            return redirect("student_history")
            
        except Student.DoesNotExist:
            messages.error(request, "Student profile not found.")
            return redirect("student_registration")
        except Exception as e:
            messages.error(request, f"Error submitting rating: {str(e)}")
            return render(request, "student/rating.html", {
                'contract_id': contract_id,
                'employer_id': employer_id
            })
    
    # GET request - show rating form
    return render(request, "student/rating.html", {
        'contract_id': contract_id,
        'employer_id': employer_id
    })

from django.db.models import Q
from .models import Message

def student_chat(request, employer_email):
    """
    Display chat between student and employer
    """
    if "username" not in request.session:
        return redirect("login")
    
    logged_in_email = request.session.get("username")
    
    # Fetch ALL messages between this student and employer
    chat_messages = Message.objects.filter(
        Q(sender_id=logged_in_email, receiver_id=employer_email) |
        Q(sender_id=employer_email, receiver_id=logged_in_email)
    ).order_by('timestamp')
    
    # Get employer name
    employer_name = employer_email.split('@')[0].title()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT o_name, shop_name FROM employer WHERE email_id = %s",
                [employer_email]
            )
            employer_data = cursor.fetchone()
            if employer_data:
                employer_name = employer_data[1] if employer_data[1] else employer_data[0]
    except:
        pass
    
    context = {
        'messages': chat_messages,
        'current_user_id': logged_in_email,
        'employer_id': employer_email,
        'employer_name': employer_name,
    }
    
    return render(request, 'student/chat.html', context)


def send_message(request):
    """
    Handle sending messages
    """
    if "username" not in request.session:
        return redirect("login")
    
    if request.method == 'POST':
        sender_id = request.POST.get('sender_id')
        receiver_id = request.POST.get('receiver_id')
        message_text = request.POST.get('message_text')
        
        if sender_id and receiver_id and message_text:
            try:
                Message.objects.create(
                    sender_id=sender_id,
                    receiver_id=receiver_id,
                    message_text=message_text.strip(),
                    timestamp=timezone.now()
                )
                messages.success(request, 'Message sent!')
            except Exception as e:
                messages.error(request, f'Failed to send: {str(e)}')
        
        return redirect('student_chat', employer_email=receiver_id)
    
    return redirect('student_home')