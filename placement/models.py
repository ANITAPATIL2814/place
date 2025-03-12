from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class TimeStampModel(models.Model): 

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    soft_delete = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Person(TimeStampModel):

    BLOOD_TYPE = (
        ('A+', 'A-Positive'),
        ('A-', 'A-Negative'),
        ('B+', 'B-Positive'),
        ('B-', 'B-Negative'),
        ('O+', 'O-Positive'),
        ('O-', 'O-Negative'),
        ('AB+', 'AB-Positive'),
        ('AB-', 'AB-Negative'),
    )

    GENDER_TYPE = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    name = models.CharField(max_length=50, db_index=True)
    gender = models.CharField(max_length=2, null=False, choices=GENDER_TYPE, blank=True)
    dob = models.DateField(null=True, blank=True)
    phone = models.BigIntegerField(null=True, blank=True)
    curr_address = models.TextField()
    perm_address = models.TextField(null=True)
    address_flag = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='profile-images', null=True)
    blood_group = models.CharField(max_length=3, null=True, choices=BLOOD_TYPE, blank=True)
    celery_schedule = models.IntegerField(default=0)

    class Meta:
        abstract = True


class Course(TimeStampModel):

    name = models.CharField(max_length=100, null=False, db_index=True, unique=True)
    abbr = models.CharField(max_length=20, db_index=True, unique=True)
    duration = models.IntegerField()

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return str(self.name)

from django.contrib.auth.models import User
from django.db import models

class Student(Person):
    GUARDIAN_TYPE = (
        ('F', 'Father'),
        ('M', 'Mother'),
        ('G', 'Guardian')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    roll_no = models.SlugField(unique=True)
    guardian_name = models.CharField(max_length=50)
    guardian_type = models.CharField(max_length=1, choices=GUARDIAN_TYPE)
    guardian_phone = models.CharField(max_length=15, null=True, blank=True)
    course = models.ForeignKey('Course', db_index=True, on_delete=models.CASCADE)
    batch = models.IntegerField()
    email = models.CharField(max_length=100, null=False, unique=True)

    def __str__(self):
        return f"{self.roll_no} - {self.name}"

class StudentRegister(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_register')
    email = models.EmailField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.user.username} - {self.email}"  
         
class StudentAcademic(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='academic_info')
    tenth_percentage = models.FloatField()
    twelfth_percentage = models.FloatField()
    graduation_percentage = models.FloatField()
    extra_courses = models.TextField()

    def __str__(self):
        return f"{self.student.name}'s Academic Info"
from django.db import models

class Employee(models.Model):
    e_id = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    dob = models.DateField()
    phone = models.BigIntegerField(null=True, blank=True)
    blood_group = models.CharField(max_length=5)
    student_permit = models.BooleanField(default=False)
    placement_permit = models.BooleanField(default=False)
    company_permit = models.BooleanField(default=False)
    soft_delete = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)

    def __str__(self):
        return self.name


class Company(TimeStampModel):

    name = models.CharField(max_length=200, db_index=True)
    address = models.TextField()
    phone = models.BigIntegerField(null=True, blank=True)
    contact_person = models.CharField(max_length=100, db_index=True)
    email = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name + '-' + str(self.contact_person))

    def __unicode__(self):
        return str(self.name + '-' + str(self.contact_person))

from placement.models import Company  
class CampusDrive(TimeStampModel):

    company = models.ForeignKey(Company, db_index=True, on_delete=models.CASCADE)
    drive_year = models.IntegerField()
    package = models.CharField(max_length=10, db_index=True)
    bond_period = models.IntegerField()
    dateofdrive = models.DateField(null=False, blank=True)

    def __str__(self):
        return str(str(self.company) + '-' + str(self.drive_year))

    def __unicode__(self):
        return str(str(self.company) + '-' + str(self.drive_year))


class Placements(TimeStampModel):

    student = models.ForeignKey(Student, db_index=True, on_delete=models.CASCADE)
    campus_drive = models.ForeignKey(CampusDrive, on_delete=models.CASCADE)
    dateofjoining = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(str(self.student) + '-' + str(self.campus_drive))

    def __unicode__(self):
        return str(str(self.student) + '-' + str(self.campus_drive))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "campus_drive"], name="unique_student_campus_drive")
        ]


class History(TimeStampModel):

    user = models.ForeignKey(Employee, on_delete=models.CASCADE)
    activity = models.TextField(null=True, blank=True)
    activity_type = models.CharField(max_length=50)

    def __str__(self):
        return str(str(self.user) + '-' + self.activity_type)

    def __unicode__(self):
        return str(str(self.user) + '-' + self.activity_type)


class PasswordReset(TimeStampModel):

    user = models.ForeignKey(Employee, on_delete=models.CASCADE)
    password_request_created_at = models.DateTimeField(auto_now_add=True)
    token = models.TextField()
    token_consumed = models.BooleanField(default=False)

    def __str__(self):
        return str(str(self.user) + '-' + str(self.token_consumed))

    def __unicode__(self):
        return str(str(self.user) + '-' + str(self.token_consumed))