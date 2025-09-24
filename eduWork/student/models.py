from django.db import models
# from employer.models import Contract
# Create your models here.
class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    f_name = models.CharField(max_length=45)
    l_name = models.CharField(max_length=45)
    age = models.IntegerField()
    skill = models.CharField(max_length=500)
    dob = models.DateField()
    gender = models.CharField(max_length=45)
    address = models.CharField(max_length=500)
    phone_no = models.CharField(max_length=10)
    email_id = models.CharField(max_length=45)
    photo = models.CharField(max_length=4000)  # or ImageField if you want uploads

    class Meta:
        db_table='student'

class Announcement(models.Model):
    announcement_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500)
    date = models.DateField()
    time = models.TimeField()

    class Meta:
        db_table = 'announcement'

from django.db import models

class Jobs(models.Model):
    job_post_id = models.AutoField(primary_key=True)
    post_title=models.CharField(max_length=45)
    post_description=models.CharField(max_length=500)
    post_date=models.DateField()
    shop_name=models.CharField(max_length=45)
    phone_no=models.CharField(max_length=45)
    vacancy=models.IntegerField()
    map_loc=models.CharField(max_length=200)
    start_date=models.DateField()
    end_date=models.DateField()
    student_id=models.CharField(max_length=45)
    salary=models.CharField(max_length=5)

    class Meta:
        db_table = 'job_post'

class JobHistory(models.Model):
    log_id = models.AutoField(primary_key=True)
    contract_id = models.CharField(max_length=45)
    student_id = models.CharField(max_length=45)
    employer_id = models.CharField(max_length=45)
    join_date = models.DateField()
    leaving_date = models.DateField()
    total_salary = models.CharField(max_length=6)

    class Meta:
        db_table = 'job_history'


    