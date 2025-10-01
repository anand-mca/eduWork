from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from datetime import datetime

def admin_login(request):
    """
    Admin login view
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        # Check admin credentials (you should use environment variables for production)
        if username == "admin" and password == "admin123":
            request.session["admin_logged_in"] = True
            request.session["admin_username"] = username
            return redirect("admin_home")
        else:
            return render(request, "admin/admin_login.html", {
                "error": "Invalid admin credentials"
            })
    
    return render(request, "admin/admin_login.html")


def admin_logout(request):
    """
    Admin logout view
    """
    request.session.flush()
    return redirect("admin_login")


def admin_home(request):
    """
    Admin dashboard with statistics
    """
    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")
    
    try:
        with connection.cursor() as cursor:
            # Get total counts
            cursor.execute("SELECT COUNT(*) FROM student")
            total_students = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM employer")
            total_employers = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM job_post")
            total_jobs = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM announcement")
            total_announcements = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM feedback")
            total_feedbacks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM contract WHERE status='active'")
            active_contracts = cursor.fetchone()[0]
            
            stats = {
                'total_students': total_students,
                'total_employers': total_employers,
                'total_jobs': total_jobs,
                'total_announcements': total_announcements,
                'total_feedbacks': total_feedbacks,
                'active_contracts': active_contracts
            }
        
        return render(request, "admin/admin_home.html", {"stats": stats})
        
    except Exception as e:
        messages.error(request, f"Error loading dashboard: {str(e)}")
        return render(request, "admin/admin_home.html", {"stats": {}})


def manage_students(request):
    """
    View and manage all students
    """
    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT student_id, f_name, l_name, email_id, phone_no, age, skill, address
                FROM student
                ORDER BY student_id DESC
            """)
            students_data = cursor.fetchall()
            
            students = []
            for row in students_data:
                student_dict = {
                    'student_id': row[0],
                    'f_name': row[1],
                    'l_name': row[2],
                    'email_id': row[3],
                    'phone_no': row[4],
                    'age': row[5],
                    'skill': row[6],
                    'address': row[7]
                }
                students.append(student_dict)
        
        return render(request, "admin/manage_students.html", {"students": students})
        
    except Exception as e:
        messages.error(request, f"Error loading students: {str(e)}")
        return render(request, "admin/manage_students.html", {"students": []})


def delete_student(request, student_id):
    """
    Delete a student and their login credentials
    """
    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")
    
    if request.method == "POST":
        try:
            with connection.cursor() as cursor:
                # Get student email before deletion
                cursor.execute("SELECT email_id FROM student WHERE student_id = %s", [student_id])
                student_data = cursor.fetchone()
                
                if student_data:
                    email_id = student_data[0]
                    
                    # Delete from login table
                    cursor.execute("DELETE FROM login WHERE username = %s", [email_id])
                    
                    # Delete related records first (to avoid foreign key issues)
                    cursor.execute("DELETE FROM academic WHERE student_id = %s", [email_id])
                    cursor.execute("DELETE FROM rating WHERE student_id = %s", [email_id])
                    
                    # Delete student
                    cursor.execute("DELETE FROM student WHERE student_id = %s", [student_id])
                    
                    messages.success(request, f"Student deleted successfully!")
                else:
                    messages.error(request, "Student not found.")
                    
        except Exception as e:
            messages.error(request, f"Error deleting student: {str(e)}")
    
    return redirect("manage_students")


def manage_employers(request):
    """
    View and manage all employers
    """
    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT employer_id, o_name, shop_name, category, email_id, phone_no, address
                FROM employer
                ORDER BY employer_id DESC
            """)
            employers_data = cursor.fetchall()
            
            employers = []
            for row in employers_data:
                employer_dict = {
                    'employer_id': row[0],
                    'o_name': row[1],
                    'shop_name': row[2],
                    'category': row[3],
                    'email_id': row[4],
                    'phone_no': row[5],
                    'address': row[6]
                }
                employers.append(employer_dict)
        
        return render(request, "admin/manage_employers.html", {"employers": employers})
        
    except Exception as e:
        messages.error(request, f"Error loading employers: {str(e)}")
        return render(request, "admin/manage_employers.html", {"employers": []})


def delete_employer(request, employer_id):
    """
    Delete an employer and their login credentials
    """
    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")
    
    if request.method == "POST":
        try:
            with connection.cursor() as cursor:
                # Get employer email before deletion
                cursor.execute("SELECT email_id FROM employer WHERE employer_id = %s", [employer_id])
                employer_data = cursor.fetchone()
                
                if employer_data:
                    email_id = employer_data[0]
                    
                    # Delete from login table
                    cursor.execute("DELETE FROM login WHERE username = %s", [email_id])
                    
                    # Delete related job posts
                    cursor.execute("DELETE FROM job_post WHERE employer_id = %s", [employer_id])
                    
                    # Delete related ratings
                    cursor.execute("DELETE FROM rating WHERE employer_id = %s", [email_id])
                    
                    # Delete employer
                    cursor.execute("DELETE FROM employer WHERE employer_id = %s", [employer_id])
                    
                    messages.success(request, f"Employer deleted successfully!")
                else:
                    messages.error(request, "Employer not found.")
                    
        except Exception as e:
            messages.error(request, f"Error deleting employer: {str(e)}")
    
    return redirect("manage_employers")


def manage_jobs(request):
    """
    View and delete job posts
    """
    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT jp.job_post_id, jp.post_title, jp.post_description, 
                       jp.shop_name, jp.vacancy, jp.start_date, jp.end_date, 
                       jp.salary, jp.post_date, e.o_name
                FROM job_post jp
                LEFT JOIN employer e ON jp.employer_id = e.employer_id
                ORDER BY jp.post_date DESC
            """)
            jobs_data = cursor.fetchall()
            
            jobs = []
            for row in jobs_data:
                job_dict = {
                    'job_post_id': row[0],
                    'post_title': row[1],
                    'post_description': row[2],
                    'shop_name': row[3],
                    'vacancy': row[4],
                    'start_date': row[5],
                    'end_date': row[6],
                    'salary': row[7],
                    'post_date': row[8],
                    'employer_name': row[9] if row[9] else 'Unknown'
                }
                jobs.append(job_dict)
        
        return render(request, "admin/manage_jobs.html", {"jobs": jobs})
        
    except Exception as e:
        messages.error(request, f"Error loading jobs: {str(e)}")
        return render(request, "admin/manage_jobs.html", {"jobs": []})


def delete_job(request, job_id):
    """
    Delete a job post
    """
    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")
    
    if request.method == "POST":
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM job_post WHERE job_post_id = %s", [job_id])
                messages.success(request, "Job post deleted successfully!")
                
        except Exception as e:
            messages.error(request, f"Error deleting job: {str(e)}")
    
    return redirect("manage_jobs")


def manage_announcements(request):
    """
    View and delete announcements
    """
    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT announcement_id, title, description, date, time
                FROM announcement
                ORDER BY date DESC, time DESC
            """)
            announcements_data = cursor.fetchall()
            
            announcements = []
            for row in announcements_data:
                announcement_dict = {
                    'announcement_id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'date': row[3],
                    'time': row[4]
                }
                announcements.append(announcement_dict)
        
        return render(request, "admin/manage_announcements.html", {"announcements": announcements})
        
    except Exception as e:
        messages.error(request, f"Error loading announcements: {str(e)}")
        return render(request, "admin/manage_announcements.html", {"announcements": []})


def delete_announcement(request, announcement_id):
    """
    Delete an announcement
    """
    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")
    
    if request.method == "POST":
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM announcement WHERE announcement_id = %s", [announcement_id])
                messages.success(request, "Announcement deleted successfully!")
                
        except Exception as e:
            messages.error(request, f"Error deleting announcement: {str(e)}")
    
    return redirect("manage_announcements")


def view_feedbacks(request):
    """
    View all feedbacks from students or employers
    """
    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT f.feedback_id, f.feedback, f.date, f.time, f.u_id,
                       s.f_name, s.l_name,
                       e.o_name, e.shop_name
                FROM feedback f
                LEFT JOIN student s ON f.u_id = s.email_id
                LEFT JOIN employer e ON f.u_id = e.email_id
                ORDER BY f.date DESC, f.time DESC
            """)
            feedbacks_data = cursor.fetchall()
            
            feedbacks = []
            for row in feedbacks_data:
                # student fields
                student_fname = row[5]
                student_lname = row[6]
                # employer fields
                employer_name = row[7]
                shop_name = row[8]

                if student_fname and student_lname:
                    user_name = f"{student_fname} {student_lname}"
                elif employer_name:
                    user_name = f"{employer_name} ({shop_name})" if shop_name else employer_name
                else:
                    user_name = "Anonymous"
                
                feedback_dict = {
                    'feedback_id': row[0],
                    'feedback': row[1],
                    'date': row[2],
                    'time': row[3],
                    'user_id': row[4],
                    'student_name': user_name
                }
                feedbacks.append(feedback_dict)
        
        return render(request, "admin/view_feedbacks.html", {"feedbacks": feedbacks})
        
    except Exception as e:
        messages.error(request, f"Error loading feedbacks: {str(e)}")
        return render(request, "admin/view_feedbacks.html", {"feedbacks": []})
