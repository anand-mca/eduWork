from django.db import models
from student.models import Jobs

class Employer(models.Model):
    employer_id=models.AutoField(primary_key=True)
    o_name=models.CharField(max_length=45)
    shop_name=models.CharField(max_length=45)
    category=models.CharField(max_length=500)
    address=models.CharField(max_length=500)
    phone_no=models.CharField(max_length=10)
    email_id=models.CharField(max_length=45)
    photo=models.CharField(max_length=4000) # or ImageField if you want uploads
    map_loc=models.CharField(max_length=500)

    class Meta:
        db_table='employer'

class Contract(models.Model):
    contract_id=models.AutoField(primary_key=True)
    post_id=models.CharField(max_length=45)
    student_id=models.CharField(max_length=45)
    employer_id=models.CharField(max_length=45)
    status=models.CharField(max_length=45)
    salary=models.CharField(max_length=5)
    student_name=models.CharField(max_length=45)
    shop_name=models.CharField(max_length=45)

    class Meta:
        db_table='contract'