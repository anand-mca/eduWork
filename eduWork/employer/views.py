from django.db import connection
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Employer, Contract
from datetime import date
from datetime import datetime
from collections import defaultdict  # Add this import

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

def update_employer(request):
    """
    Update employer profile - all fields are optional
    """
    if "username" not in request.session:
        return redirect("employer_login")
    
    logged_in_email = request.session.get("username")
    
    if request.method == 'POST':
        try:
            # Get the employer object
            employer = Employer.objects.get(email_id=logged_in_email)
            
            # Track if any field was updated
            fields_updated = []
            
            # Update only the fields that have values
            owner_name = request.POST.get('ownerName', '').strip()
            if owner_name:
                employer.o_name = owner_name
                fields_updated.append('Owner Name')
            
            shop_name = request.POST.get('shopName', '').strip()
            if shop_name:
                employer.shop_name = shop_name
                # Update session as well
                request.session['shop_name'] = shop_name
                fields_updated.append('Shop Name')
            
            category = request.POST.get('category', '').strip()
            if category:
                employer.category = category
                fields_updated.append('Category')
            
            address = request.POST.get('address', '').strip()
            if address:
                employer.address = address
                # Update session as well
                request.session['address'] = address
                fields_updated.append('Address')
            
            # Handle file upload
            if 'shopLogo' in request.FILES:
                photo = request.FILES['shopLogo']
                employer.photo = photo.name
                fields_updated.append('Shop Logo')
            
            phone = request.POST.get('phone', '').strip()
            if phone:
                employer.phone_no = phone
                # Update session as well
                request.session['phone_no'] = phone
                fields_updated.append('Phone')
            
            location_link = request.POST.get('locationLink', '').strip()
            if location_link:
                employer.map_loc = location_link
                # Update session as well
                request.session['map_loc'] = location_link
                fields_updated.append('Location Link')
            
            # Handle password update
            password = request.POST.get('password', '').strip()
            confirm_password = request.POST.get('confirmPassword', '').strip()
            
            if password or confirm_password:
                if password != confirm_password:
                    messages.error(request, "Passwords do not match!")
                    return redirect('update_profile')
                
                if password:
                    # Update password in login table
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "UPDATE login SET password = %s WHERE username = %s",
                            [password, logged_in_email]
                        )
                    fields_updated.append('Password')
            
            # Save the employer object only if there were updates
            if fields_updated:
                employer.save()
                messages.success(request, f"Profile updated successfully! Updated: {', '.join(fields_updated)}")
            else:
                messages.info(request, "No changes were made to your profile.")
            
            return redirect('employer_profile')
            
        except Employer.DoesNotExist:
            messages.error(request, "Employer profile not found.")
            return redirect('employer_login')
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")
            return redirect('update_profile')
    
    # GET request - display the form with current data
    try:
        employer = Employer.objects.get(email_id=logged_in_email)
        return render(request, 'employer/profile_update.html', {'employer': employer})
    except Employer.DoesNotExist:
        messages.error(request, "Employer profile not found.")
        return redirect('employer_login')

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
            
            return redirect("employer_home")  # Changed from render to redirect
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
                        # Check if this application is already accepted
                        cursor.execute("""
                            SELECT status FROM contract 
                            WHERE post_id = %s AND student_id = %s
                        """, [job[0], email])
                        contract_status = cursor.fetchone()
                        
                        applicant = {
                            'student_id': student_data[0],
                            'student_name': f"{student_data[1]} {student_data[2]}",
                            'student_email': student_data[3],
                            'student_phone': student_data[4],
                            'application_id': f"{job[0]}_{email}",  # composite ID with email
                            'is_accepted': contract_status and contract_status[0] == 'active'
                        }
                        job_dict['applicants'].append(applicant)
            
            job_posts.append(job_dict)
    
    return render(request, "employer/view_applications.html", {"job_posts": job_posts})

def delete_job_post(request, job_post_id):
    if "username" not in request.session:
        return redirect("login")
    
    # Use raw SQL since you don't have JobPost model imported
    with connection.cursor() as cursor:
        if request.method == "POST":
            cursor.execute("DELETE FROM job_post WHERE job_post_id = %s", [job_post_id])
            messages.success(request, "Job post deleted successfully.")
            return redirect("view_applications")

    messages.error(request, "Invalid request.")
    return redirect("view_applications")

def accept_application(request):
    if "username" not in request.session:
        return redirect("login")
    
    if request.method == "POST":
        application_id = request.POST.get("application_id")
        
        # Parse the application_id to get job_id and student_email
        try:
            job_id, student_email = application_id.split("_", 1)
            job_id = int(job_id)
        except ValueError:
            messages.error(request, "Invalid application ID.")
            return redirect("view_applications")
        
        with connection.cursor() as cursor:
            # Get job details (salary, shop_name, and current vacancy)
            cursor.execute("""
                SELECT salary, shop_name, vacancy
                FROM job_post 
                WHERE job_post_id = %s
            """, [job_id])
            job_data = cursor.fetchone()
            
            if not job_data:
                messages.error(request, "Job not found.")
                return redirect("view_applications")
            
            salary, shop_name, current_vacancy = job_data
            
            # Check if there are still vacancies available
            if current_vacancy <= 0:
                messages.error(request, "No vacancies left for this position.")
                return redirect("view_applications")
            
            employer_email = request.session.get("username")
            
            # Get student name
            cursor.execute("""
                SELECT f_name, l_name
                FROM student 
                WHERE email_id = %s
            """, [student_email])
            student_data = cursor.fetchone()
            
            if not student_data:
                messages.error(request, "Student not found.")
                return redirect("view_applications")
            
            student_name = f"{student_data[0]} {student_data[1]}"
            
            # Check if contract already exists
            cursor.execute("""
                SELECT contract_id 
                FROM contract 
                WHERE post_id = %s AND student_id = %s
            """, [job_id, student_email])
            existing_contract = cursor.fetchone()
            
            if existing_contract:
                messages.info(request, "Application already processed.")
                return redirect("view_applications")
            
            # Insert new contract with student_name and shop_name
            cursor.execute("""
                INSERT INTO contract 
                (post_id, student_id, employer_id, status, salary, student_name, shop_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [job_id, student_email, employer_email, "active", salary, student_name, shop_name])
            
            # Decrement vacancy count when application is accepted
            cursor.execute("""
                UPDATE job_post 
                SET vacancy = vacancy - 1 
                WHERE job_post_id = %s
            """, [job_id])
            
            messages.success(request, f"Application accepted successfully! Vacancy updated: {current_vacancy - 1} remaining.")
    
    return redirect("view_applications")

def view_contract(request):
    if "username" not in request.session:
        return redirect("login")
    
    employer_email = request.session.get("username")
    
    with connection.cursor() as cursor:
        # Get all contracts for this employer along with job details for start/end dates
        cursor.execute("""
            SELECT c.contract_id, c.post_id, c.student_id, c.status, c.salary, 
                   c.student_name, c.shop_name, jp.start_date, jp.end_date
            FROM contract c
            LEFT JOIN job_post jp ON c.post_id = jp.job_post_id
            WHERE c.employer_id = %s AND c.status = 'active'
            ORDER BY c.contract_id DESC
        """, [employer_email])
        
        contracts_data = cursor.fetchall()
        
        contracts = []
        for contract in contracts_data:
            contract_dict = {
                'contract_id': contract[0],
                'post_id': contract[1],
                'student_id': contract[2],
                'status': contract[3],
                'salary': contract[4],
                'student_name': contract[5] or 'Unknown Student',
                'shop_name': contract[6] or 'Unknown Shop',
                'start_date': contract[7] or 'N/A',
                'end_date': contract[8] or 'N/A'
            }
            contracts.append(contract_dict)
    
    return render(request, "employer/view_contract.html", {"contracts": contracts})

def terminate_contract(request, contract_id):
    if "username" not in request.session:
        return redirect("login")
    
    employer_email = request.session.get("username")
    
    if request.method == "POST":
        with connection.cursor() as cursor:
            # Verify this contract belongs to the logged-in employer and get contract details
            cursor.execute("""
                SELECT c.contract_id, c.student_id, c.employer_id, c.post_id, c.salary,
                       jp.start_date, jp.salary as job_salary
                FROM contract c
                JOIN job_post jp ON c.post_id = jp.job_post_id
                WHERE c.contract_id = %s AND c.employer_id = %s
            """, [contract_id, employer_email])
            
            contract_data = cursor.fetchone()
            
            if contract_data:
                # Extract contract details
                contract_id = contract_data[0]
                student_id = contract_data[1]  # student email
                employer_id = contract_data[2]  # employer email
                post_id = contract_data[3]
                contract_salary = contract_data[4]
                join_date = contract_data[5]  # start_date from job_post
                job_salary = contract_data[6]
                
                # Get current date for leaving date
                from datetime import date
                current_date = date.today()
                
                # Calculate working days (including both start and end dates)
                working_days = (current_date - join_date).days + 1
                
                # Ensure working days is at least 1 (in case of same day termination)
                if working_days < 1:
                    working_days = 1
                
                # Use contract salary if available, otherwise use job salary
                daily_salary = int(contract_salary) if contract_salary else int(job_salary)
                
                # Calculate total salary
                total_salary = working_days * daily_salary
                
                # Insert into job_history table
                cursor.execute("""
                    INSERT INTO job_history (contract_id, student_id, employer_id, 
                                           join_date, leaving_date, total_salary)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, [
                    contract_id,
                    student_id,     # student email
                    employer_id,    # employer email  
                    join_date,      # start_date from job_post
                    current_date,   # current date when terminate button is pressed
                    str(total_salary)  # calculated total salary
                ])
                
                # Increment vacancy in job_post (make position available again)
                cursor.execute("""
                    UPDATE job_post 
                    SET vacancy = vacancy + 1 
                    WHERE job_post_id = %s
                """, [post_id])
                
                # Delete the contract (as per original logic)
                cursor.execute("DELETE FROM contract WHERE contract_id = %s", [contract_id])
                
                messages.success(request, 
                    f"Contract terminated successfully. "
                    f"Job history recorded: {working_days} working days, "
                    f"Total salary: ₹{total_salary}")
            else:
                messages.error(request, "Contract not found or you don't have permission to terminate it.")
    
    return redirect("view_contract")

def view_history(request):
    """
    View to display job history of a specific student for the employer
    """
    if "username" not in request.session:
        return redirect("login")
    
    student_id = request.GET.get('student_id')
    
    if not student_id:
        messages.error(request, "Student ID is required to view history.")
        return redirect("view_applications")
    
    try:
        with connection.cursor() as cursor:
            # Get student information
            cursor.execute("""
                SELECT student_id, f_name, l_name, email_id, phone_no, skill, age
                FROM student 
                WHERE student_id = %s
            """, [student_id])
            student_data = cursor.fetchone()
            
            if not student_data:
                messages.error(request, "Student not found.")
                return redirect("view_applications")
            
            student_info = {
                'student_id': student_data[0],
                'name': f"{student_data[1]} {student_data[2]}",
                'email': student_data[3],
                'phone': student_data[4],
                'skills': student_data[5],
                'age': student_data[6]
            }
            
            # Get job history for this student with job details
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
            """, [student_info['email']])
            
            history_data = cursor.fetchall()
            
            # Convert to list of dictionaries for easier template usage
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
                    'daily_rate': salary // working_days if working_days > 0 else 0
                }
                job_history.append(history_dict)
            
            # Calculate summary statistics
            experience_summary = {
                'total_jobs': total_jobs,
                'total_experience_days': total_experience_days,
                'total_earnings': total_earnings,
                'average_job_duration': total_experience_days // total_jobs if total_jobs > 0 else 0,
                'average_daily_rate': total_earnings // total_experience_days if total_experience_days > 0 else 0
            }
        
        return render(request, "employer/view_history.html", {
            "student_info": student_info,
            "job_history": job_history,
            "experience_summary": experience_summary
        })
        
    except Exception as e:
        messages.error(request, f"Error loading student history: {str(e)}")
        return redirect("view_applications")
    
def view_log(request):
    """
    View to display work log - all job history records for the employer
    """
    if "username" not in request.session:
        return redirect("login")
    
    employer_email = request.session.get("username")
    
    try:
        with connection.cursor() as cursor:
            # Get all job history records for this employer with student names
            cursor.execute("""
                SELECT jh.log_id, jh.contract_id, jh.student_id, jh.employer_id,
                       jh.join_date, jh.leaving_date, jh.total_salary,
                       s.f_name, s.l_name
                FROM job_history jh
                LEFT JOIN student s ON jh.student_id = s.email_id
                WHERE jh.employer_id = %s
                ORDER BY jh.log_id ASC
            """, [employer_email])
            
            history_data = cursor.fetchall()
            
            # Convert to list of dictionaries for template
            work_logs = []
            for index, row in enumerate(history_data, 1):
                student_name = f"{row[7]} {row[8]}" if row[7] and row[8] else "Unknown Student"
                
                log_dict = {
                    'sl_no': index,
                    'student_name': student_name,
                    'join_date': row[4],
                    'leaving_date': row[5],
                    'total_salary': f"₹{row[6]}" if row[6] else "₹0"
                }
                work_logs.append(log_dict)
    
        return render(request, "employer/view_log.html", {
            "work_logs": work_logs
        })
        
    except Exception as e:
        messages.error(request, f"Error loading work log: {str(e)}")
        return redirect("employer_home")

def view_rating(request):
    """
    View to display ratings and reviews for the logged-in employer
    """
    if "username" not in request.session:
        return redirect("login")
    
    employer_email = request.session.get("username")
    
    try:
        with connection.cursor() as cursor:
            # Get all ratings for this employer with student names
            cursor.execute("""
                SELECT r.rating_id, r.student_id, r.employer_id, r.contract_id,
                       r.star, r.description, r.date_time,
                       s.f_name, s.l_name
                FROM rating r
                LEFT JOIN student s ON r.student_id = s.email_id
                WHERE r.employer_id = %s
                ORDER BY r.date_time DESC
            """, [employer_email])
            
            ratings_data = cursor.fetchall()
            
            # Calculate statistics
            total_reviews = len(ratings_data)
            if total_reviews == 0:
                context = {
                    'total_reviews': 0,
                    'average_rating': 0,
                    'customer_satisfaction': 0,
                    'this_month_reviews': 0,
                    'positive_reviews': 0,
                    'neutral_reviews': 0,
                    'negative_reviews': 0,
                    'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                    'recent_reviews': []
                }
                return render(request, "employer/view_rating.html", context)
            
            # Calculate rating statistics
            total_stars = sum(row[4] for row in ratings_data)
            average_rating = round(total_stars / total_reviews, 1)
            
            # Count ratings by star level
            rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for row in ratings_data:
                rating_counts[row[4]] += 1
            
            # Calculate percentages for rating distribution
            rating_distribution = {}
            for star in range(1, 6):
                percentage = (rating_counts[star] / total_reviews) * 100 if total_reviews > 0 else 0
                rating_distribution[star] = {
                    'count': rating_counts[star],
                    'percentage': round(percentage, 1)
                }
            
            # Count positive (4-5), neutral (3), negative (1-2) reviews
            positive_reviews = rating_counts[4] + rating_counts[5]
            neutral_reviews = rating_counts[3]
            negative_reviews = rating_counts[1] + rating_counts[2]
            
            # Calculate customer satisfaction percentage (4-5 star reviews)
            customer_satisfaction = round((positive_reviews / total_reviews) * 100, 1) if total_reviews > 0 else 0
            
            # Count this month's reviews
            from datetime import datetime, timedelta
            current_date = datetime.now()
            first_day_of_month = current_date.replace(day=1)
            
            this_month_count = 0
            for row in ratings_data:
                if row[6] and row[6] >= first_day_of_month:
                    this_month_count += 1
            
            # Prepare recent reviews for display
            recent_reviews = []
            for row in ratings_data[:10]:  # Show last 10 reviews
                student_name = f"{row[7]} {row[8]}" if row[7] and row[8] else "Anonymous Student"
                
                review_dict = {
                    'rating_id': row[0],
                    'student_name': student_name,
                    'contract_id': row[3],
                    'star_rating': row[4],
                    'description': row[5],
                    'date_time': row[6],
                    'stars_display': '★' * row[4] + '☆' * (5 - row[4])  # Visual stars
                }
                recent_reviews.append(review_dict)
            
            context = {
                'total_reviews': total_reviews,
                'average_rating': average_rating,
                'customer_satisfaction': customer_satisfaction,
                'this_month_reviews': this_month_count,
                'positive_reviews': positive_reviews,
                'neutral_reviews': neutral_reviews,
                'negative_reviews': negative_reviews,
                'rating_distribution': rating_distribution,
                'recent_reviews': recent_reviews
            }
        
        return render(request, "employer/view_rating.html", context)
        
    except Exception as e:
        messages.error(request, f"Error loading ratings: {str(e)}")
        return redirect("employer_home")
    
from django.db.models import Q
from django.db import connection
from django.utils import timezone
from django.contrib import messages
from .models import Message

def employer_chat(request, student_email):
    """
    Display chat between employer and student
    """
    if "username" not in request.session:  # Changed from "email"
        return redirect("employer_login")
    
    logged_in_email = request.session.get("username")  # Changed from "email"
    
    # Fetch ALL messages between this employer and student
    chat_messages = Message.objects.filter(
        Q(sender_id=logged_in_email, receiver_id=student_email) |
        Q(sender_id=student_email, receiver_id=logged_in_email)
    ).order_by('timestamp')
    
    # Get student name from student table
    student_name = student_email.split('@')[0].title()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT f_name, l_name FROM student WHERE email_id = %s",
                [student_email]
            )
            student_data = cursor.fetchone()
            if student_data:
                student_name = f"{student_data[0]} {student_data[1]}"
    except:
        pass
    
    context = {
        'messages': chat_messages,
        'current_user_id': logged_in_email,
        'student_id': student_email,
        'student_name': student_name,
    }
    
    return render(request, 'employer/chat.html', context)


def employer_send_message(request):
    """
    Handle sending messages from employer
    """
    if "username" not in request.session:  # Changed from "email"
        return redirect("employer_login")
    
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
        
        return redirect('employer_chat', student_email=receiver_id)
    
    return redirect('employer_home')

from .models import Feedback
from datetime import datetime

def post_feedback(request):
    """
    View to handle employer feedback submission
    """
    if "username" not in request.session:
        return redirect("employer_login")
    
    logged_in_email = request.session.get("username")
    
    if request.method == "POST":
        feedback_text = request.POST.get("feedback")
        
        if feedback_text and feedback_text.strip():
            try:
                # Create new feedback entry
                current_date = datetime.now().date()
                current_time = datetime.now().time()
                
                Feedback.objects.create(
                    feedback=feedback_text.strip(),
                    date=current_date,
                    time=current_time,
                    u_id=logged_in_email
                )
                
                messages.success(request, "Thank you for your feedback! It helps us improve EduWork.")
                return redirect("employer_post_feedback")
                
            except Exception as e:
                messages.error(request, f"Error submitting feedback: {str(e)}")
        else:
            messages.error(request, "Please enter your feedback before submitting.")
    
    return render(request, "employer/post_feedback.html")