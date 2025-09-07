from django.db import models

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



    