from django.urls import reverse
import six
# from django.shortcuts import render
from django.shortcuts import redirect, render
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
    Http404
)

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from placement import models
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.conf import settings
from django.core.cache import cache
from placement.helpers import context_helper
from django.template.context import RequestContext
from django.contrib.auth.models import User
from django.db.models import Q
from django.core import serializers
import json
from django.db.models.query_utils import Q
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import  timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template import loader
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from placement_portal.settings import DEFAULT_FROM_EMAIL
from django.views.generic import *
from string import ascii_letters, digits
from datetime import datetime, timedelta
import hashlib
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .models import Student
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from .forms import RegisterForm, LoginForm
from .models import Student

def Student_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            student = form.save(commit=False)
            student.user = user
            student.save()
            auth_login(request, user)
            return redirect('studlogin')
    else:
        form = RegisterForm()
    return render(request, 'stu_regi.html', {'form': form})

# Register View
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            student = form.save(commit=False)
            student.user = user
            student.save()
            auth_login(request, user)
            return redirect('studlogin')
    else:
        form = RegisterForm()
    return render(request, 'student_registration.html', {'form': form})

# Login View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from .forms import LoginForm  # Ensure this import works

# Login View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from .forms import LoginForm  # Ensure this import works

def studlogin_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['Email']  # Use 'email' instead of 'username'
            password = form.cleaned_data['Password']  # Use 'password'
            user = authenticate(username=email, password=password)  # Ensure the username is correct
            if user is not None:
                auth_login(request, user)
                return redirect('student_dashboard')
            else:
                form.add_error(None, 'Invalid credentials')
    else:
        form = LoginForm()
    return render(request, 'student_login.html', {'form': form})

# Student Dashboard
def student_dashboard(request):
    if request.user.is_authenticated:
        student = Student.objects.get(user=request.user)
        return render(request, 'student_dashboard.html', {'student': student})
    else:
        return redirect('login')
    
@login_required
def view_profile(request):
    # Assuming the student is the current logged-in user
    student = models.Student.objects.get(user=request.user)

    # Pass the student object to the template
    return render(request, 'view_profile.html', {'student': student})


def mypage(request):
    form = AddForm(request.POST or None)
    if form.is_valid():
        form.save()
    return render(request, "add.html", {'form':form})


def handler404(request):
    response = render_to_response('404.html', {}, 
        context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('500.html', {}, 
        context_instance=RequestContext(request))
    response.status_code = 500
    return response


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('home')
    return HttpResponseRedirect('login')


@login_required
def change_password(request):

    emp = models.Employee.objects.get(user=request.user)
    context_dict = {}
    if request.method == 'POST':
        form = AdminPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            context_dict["message"] = "Password changed successfully"
            history = models.History(
                user=emp,
                activity="",
                activity_type="Changed password"
            )
            history.save()
        else:
            context_dict["message"] = "Password not changed"
    return render(request, "ChangePassword.html", context_dict)

@login_required
def home(request):
    context_dict = {}
    employee = models.Employee.objects.filter(user=request.user).first()
    
    emp_info = context_helper.get_emp_info(employee)
    if emp_info is not None:
        context_dict.update(emp_info)
    else:
        context_dict['error'] = 'Employee information not found'
    print(context_dict)  
    return render(request, "HomePage.html", context_dict)


def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('home')
    next_url = request.GET.get('next', '/home')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect(next_url)
            return render(
                request, 'index.html',
                {'message': 'Invalid login details'}
            )
    return render(request, "index.html", {})

def logout_view(request):
    logout(request)
    return redirect(reverse('login_view'))  


def password_reset(request):
    context_dict = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            user = models.Employee.objects.get(
                soft_delete=False, user__email=email
            )
            if not user:
                context_dict["message"] = "Email ID does'nt exist, Enter Correct details"
            mail = {
                'email': email,
                'domain': request.META['HTTP_HOST'],
                'site_name': 'Placement Portal',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': ''.join([random.choice(ascii_letters+digits) for i in range (128)]),
                'protocol': 'http',
            }
            try:
                reset_token = models.PasswordReset(
                    user=user,
                    token=mail['token'],
                    token_consumed=False,
                )
                reset_token.save()
            except Exception as e:
                print (e)
            subject_template_name = 'password_reset_email_subject.txt'
            email_template_name = 'password_reset_email.html'
            subject = loader.render_to_string(subject_template_name, mail)
            subject = ''.join(subject.splitlines())
            email_data = loader.render_to_string(email_template_name, mail)
            send_mail(subject, email_data, DEFAULT_FROM_EMAIL, [email], fail_silently=False)
            context_dict["message"] = "Email has been sent to your registered Email ID with instructions."
    return render(request, "password_reset_form.html", context_dict)


def password_resetenter(request, uidb64=None, token=None):
    context_dict = {}
    if request.method == 'POST':
        assert uidb64 is not None and token is not None
        uid = urlsafe_base64_decode(uidb64)
        user = models.Employee.objects.get(
            soft_delete=False, pk=uid
        )
        db_user = user.user
        reset_token = models.PasswordReset.objects.get(
            token=token, user=user
        )
        token_check = models.PasswordReset.objects.filter(
            user=user, soft_delete=False, token_consumed=False,
        ).exclude(token=token).first()
        update_fields = []
        token_check.token_consumed = True
        update_fields.append('token_consumed')
        token_check.soft_delete = True
        update_fields.append('soft_delete')
        token_check.save(update_fields=update_fields)
        time_threshold = timezone.now() - reset_token.password_request_created_at
        if time_threshold > timedelta(minutes=30):
            try:
                update_fields = []
                reset_token.token_consumed = True
                update_fields.append('token_consumed')
                reset_token.soft_delete = True
                update_fields.append('soft_delete')
                reset_token.save(update_fields=update_fields)
            except Exception as e:
                print (e)
        if reset_token.user == user and reset_token.token == token:
            if reset_token.token_consumed  == False and reset_token.soft_delete  == False:
                try:
                    update_fields = []
                    reset_token.token_consumed = True
                    update_fields.append('token_consumed')
                    reset_token.soft_delete = True
                    update_fields.append('soft_delete')
                    reset_token.save(update_fields=update_fields)
                except Exception as e:
                    print (e)
                form = AdminPasswordChangeForm(user=db_user, data=request.POST)
                if form.is_valid():
                    form.save()
                    history = models.History(
                        user=user,
                        activity = "",
                        activity_type = "Reset Password"
                    )
                    history.save()
                    context_dict["message"] = "Password changed successfully"
                else:
                    context_dict["message"] = "Password not changed"
            else:
                context_dict["message"] = "Link is no longer valid"
    return render(request, "reset.html", context_dict)




@login_required
def add_student(request):
    # Try to get an Employee record for the current user.
    try:
        emp = models.Employee.objects.get(user=request.user)
    except models.Employee.DoesNotExist:
        emp = None

    # If an Employee record exists, check for permission.
    if emp:
        if not emp.student_permit:
            raise Http404("You do not have permission to add a student.")
    else:
        # If no Employee record exists, assume this is self-registration.
        # If a student record for this user already exists, redirect to edit profile.
        existing_student = models.Student.objects.filter(user=request.user, soft_delete=False).first()
        if existing_student:
            # Redirect to the edit page for the existing student record.
            return redirect('/edit-student/' + str(existing_student.pk))

    context_dict = {
        "all_courses": context_helper.course_helper(),
        "blood_groups": context_helper.blood_group_helper(),
        "guardian_types": context_helper.guardian_type_helper(),
        "gender_type": context_helper.gender_helper(),
    }

    if request.method == 'POST':
        sname = request.POST.get('sname')
        roll = request.POST.get('rno')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender_picker')
        bgroup = request.POST.get('blood_group_picker')
        if bgroup == 'Choose option':
            bgroup = None
        phone = request.POST.get('phone')
        curradd = request.POST.get('curradd')
        permadd = request.POST.get('permadd')
        gname = request.POST.get('gname')
        course = request.POST.get('course_picker')
        batch = request.POST.get('batch')
        gtype = request.POST.get('guardian_type_picker')
        gphone = request.POST.get('gphone')
        email = request.POST.get('email')

        # Check for duplicate student based on several fields.
        duplicate_student = models.Student.objects.filter(
            name=sname,
            dob=dob,
            guardian_name=gname,
            guardian_type=gtype,
            phone=phone,
            email=email
        ).first()
        if duplicate_student:
            context_dict["message"] = 'Student already exists.'
            duplicate_student.soft_delete = False
            duplicate_student.save()
            return render(request, "AddStudent.html", context_dict)

        address_flag = request.POST.get('address_flag')
        address_flag = True if address_flag == 'on' else False
        if address_flag:
            permadd = curradd

        try:
            # Create a new student instance.
            student = models.Student(
                name=sname,
                roll_no=roll,
                dob=dob,
                gender=gender,
                blood_group=bgroup,
                phone=phone,
                curr_address=curradd,
                perm_address=permadd,
                guardian_name=gname,
                guardian_type=gtype,
                guardian_phone=gphone,
                course=models.Course.objects.get(pk=course),
                batch=batch,
                email=email,
                address_flag=address_flag,
            )
            # For self-registration, associate the student record with the current user.
            if not emp:
                student.user = request.user

            if "profile-img" in request.FILES:
                student.photo = request.FILES["profile-img"]

            student.save()

            # Record history using the Employee record if available; otherwise, use the student.
            history_user = emp if emp else student
            history = models.History(
                user=history_user,
                activity='Added roll number ' + str(roll) + '.\n',
                activity_type="add student"
            )
            history.save()

            context_dict["message"] = 'Successfully added new student.'
            context_dict["success"] = True
        except Exception as e:
            context_dict["message"] = str(e)
            context_dict["success"] = False
            print(e)

    return render(request, "AddStudent.html", context_dict)


@login_required
def add_company(request):
    context_dict = {}
    print("Logged-in user:", request.user)

    try:
        emp = models.Employee.objects.get(user=request.user)
    except models.Employee.DoesNotExist:
        print(f"Employee not found for user {request.user.username}")
        raise Http404("Employee record not found. You are not authorized to add a company.")
    
    if not emp.company_permit:
        print(f"User {request.user.username} does not have company_permit.")
        raise Http404("You do not have permission to add a company.")
    # Try to get the     Employee record for the logged-in user
    try:
        emp = models.Employee.objects.get(user=request.user)
    except models.Employee.DoesNotExist:
        # If no employee is found, raise an Http404 error
        raise Http404("Employee record not found. You are not authorized to add a company.")

    # Check if the employee has permission to add a company
    if not emp.company_permit:
        raise Http404("You do not have permission to add a company.")

    if request.method == 'POST':
        # Get the company details from the form
        cname = request.POST.get('c_name')
        c_add = request.POST.get('c_address')
        contact_person = request.POST.get('hr_name')
        c_phone = request.POST.get('c_phone')
        c_email = request.POST.get('c_email')

        # Check for a duplicate company
        duplicate_company = models.Company.objects.filter(
            name=cname, address=c_add, phone=c_phone,
            contact_person=contact_person, email=c_email,
        ).first()

        if duplicate_company:
            context_dict["message"] = 'Company already exists.'
            duplicate_company.soft_delete = False
            duplicate_company.save()
            return render(request, "AddCompany.html", context_dict)

        try:
            # Create and save the new company record
            company = models.Company(
                name=cname,
                address=c_add,
                phone=c_phone,
                contact_person=contact_person,
                email=c_email,
            )
            company.save()

            # Log the activity in the history
            history = models.History(
                user=emp,
                activity=f'Added Company: {str(cname)}.\n',
                activity_type="add company"
            )
            history.save()

            context_dict["message"] = 'Company added successfully.'
            context_dict["success"] = True
        except Exception as e:
            context_dict["message"] = str(e)
            context_dict["success"] = False
            print(e)

    return render(request, "AddCompany.html", context_dict)

@login_required
def edit_student(request, student_id):
    try:
        # Try to get an employee record for this user
        emp = models.Employee.objects.get(user=request.user)
        # If the employee does not have student_permit, deny access
        if not emp.student_permit:
            raise Http404("You do not have permission to edit student details.")
    except models.Employee.DoesNotExist:
        # If no Employee exists, assume the user is a student.
        # In that case, ensure that the student_id matches the logged in student's record.
        student = models.Student.objects.filter(user=request.user, soft_delete=False).first()
        if not student or str(student.pk) != str(student_id):
            raise Http404("You can only edit your own profile.")
    else:
        # If the user is an employee, proceed to fetch the student record to edit.
        student = models.Student.objects.filter(pk=student_id, soft_delete=False).first()
        if not student:
            raise Http404("Student not found.")

    # Build your context dictionary as before
    context_dict = {
        "all_courses": context_helper.course_helper(),
        "blood_groups": context_helper.blood_group_helper(),
        "guardian_types": context_helper.guardian_type_helper(),
        "gender_types": context_helper.gender_helper(),
        'student_id': student_id
    }
    
    if request.method == 'POST':
        # (Process form submission and update the student record)
        try:
            update_fields = []
            activity = ''
            sname = request.POST.get('sname')
            roll = request.POST.get('rno')
            dob = request.POST.get('dob')
            gender = request.POST.get('gender_picker')
            bgroup = request.POST.get('blood_group_picker')
            if bgroup == 'Choose option':
                bgroup = None
            phone = request.POST.get('phone')
            curradd = request.POST.get('curradd')
            permadd = request.POST.get('permadd')
            gname = request.POST.get('gname')
            course = request.POST.get('course_picker')
            batch = request.POST.get('batch')
            gtype = request.POST.get('guardian_type_picker')
            gphone = request.POST.get('gphone')
            email = request.POST.get('email')
            address_flag = request.POST.get('address_flag')
            address_flag = True if address_flag == 'on' else False
            if address_flag:
                permadd = curradd

            # Check if a new profile image was uploaded
            if "profile-img" in request.FILES:
                student.photo = request.FILES["profile-img"]
                update_fields.append('photo')
                activity += 'Changed photo.\n'

            if student.name != sname:
                student.name = sname
                update_fields.append('name')
                activity += f'Changed name to {sname}.\n'
            if student.roll_no != roll:
                student.roll_no = roll
                update_fields.append('roll_no')
                activity += f'Changed roll number to {roll}.\n'
            if str(student.dob) != str(dob):
                student.dob = dob
                update_fields.append('dob')
                activity += f'Changed DOB to {dob}.\n'
            if student.gender != gender:
                student.gender = gender
                update_fields.append('gender')
                activity += f'Changed gender to {gender}.\n'
            if student.blood_group != bgroup:
                student.blood_group = bgroup
                update_fields.append('blood_group')
                activity += f'Changed blood group to {bgroup}.\n'
            if student.phone != phone:
                student.phone = phone
                update_fields.append('phone')
                activity += f'Changed phone number to {phone}.\n'
            if student.curr_address != curradd:
                student.curr_address = curradd
                update_fields.append('curr_address')
                activity += f'Changed current address to {curradd}.\n'
            if student.perm_address != permadd:
                student.perm_address = permadd
                update_fields.append('perm_address')
                activity += f'Changed permanent address to {permadd}.\n'
            if student.guardian_name != gname:
                student.guardian_name = gname
                update_fields.append('guardian_name')
                activity += f'Changed guardian name to {gname}.\n'
            if student.guardian_phone != gphone:
                student.guardian_phone = gphone
                update_fields.append('guardian_phone')
                activity += f'Changed guardian phone to {gphone}.\n'
            if student.guardian_type != gtype:
                student.guardian_type = gtype
                update_fields.append('guardian_type')
                activity += f'Changed guardian type to {gtype}.\n'
            if str(student.course.pk) != str(course):
                student.course = models.Course.objects.get(pk=course)
                update_fields.append('course')
                activity += f'Changed course to {course}.\n'
            if student.batch != batch:
                student.batch = batch
                update_fields.append('batch')
                activity += f'Changed batch to {batch}.\n'
            if student.email != email:
                student.email = email
                update_fields.append('email')
                activity += f'Changed email to {email}.\n'
            if student.address_flag != address_flag:
                student.address_flag = address_flag
                update_fields.append('address_flag')
                activity += 'Changed address flag.\n'

            # Save only the updated fields
            student.save(update_fields=update_fields)

            # Record the history, using the employee if available, otherwise use the student record
            history_user = emp if 'emp' in locals() else student
            history = models.History(
                user=history_user,
                activity=activity,
                activity_type="edit student"
            )
            history.save()

            context_dict["message"] = 'Successfully updated student.'
            context_dict["success"] = True

        except Exception as e:
            context_dict["message"] = str(e)
            context_dict["success"] = False
            print(e)

    context_dict.update(context_helper.get_student_info(student))
    if isinstance(context_dict.get('dob'), str):
        from datetime import datetime
        context_dict['dob'] = datetime.strptime(context_dict['dob'], '%Y-%m-%d')
    for i in context_dict.get('course', []):
        try:
            del context_dict['all_courses'][i]
        except Exception:
            pass
    for i in context_dict.get('blood_group', []):
        try:
            context_dict['blood_groups'].remove(i)
        except Exception:
            pass
    for i in context_dict.get('guardian_type', []):
        try:
            context_dict['guardian_types'].remove(i)
        except Exception:
            pass
    for i in context_dict.get('gender_type', []):
        try:
            context_dict['gender_types'].remove(i)
        except Exception:
            pass

    if context_dict.get('success', False):
        return HttpResponseRedirect('/view-students')

    return render(request, "EditStudent.html", context_dict)



@login_required
def edit_company(request, company_id):

    emp = models.Employee.objects.get(user=request.user)
    if not emp.company_permit:
        raise Http404
    company = models.Company.objects.filter(
        pk=company_id, soft_delete=False
    ).first()
    if not company:
        raise Http404
    context_dict = {
        'company_id': company_id
    }
    if request.method == 'POST':
        update_fields = []
        activity = ''
        cname = request.POST.get('c_name')
        c_add = request.POST.get('c_address')
        contact_person = request.POST.get('hr_name')
        c_phone = request.POST.get('c_phone')
        c_email = request.POST.get('c_email')
        try:
            if company.name != cname:
                company.name = cname
                update_fields.append('name')
                activity += 'Changed company name to '+ str(cname) +'.\n'
            if company.phone != c_phone:
                company.phone = c_phone
                update_fields.append('phone')
                activity += 'Changed company phone to '+ str(c_phone) +'.\n'
            if company.address != c_add:
                company.address = c_add
                update_fields.append('address')
                activity += 'Changed company address to '+ str(c_add) +'.\n'
            if company.contact_person != contact_person:
                company.contact_person = contact_person
                update_fields.append('contact_person')
                activity += 'Changed company contact person to '+ str(contact_person) +'.\n'
            if company.email != c_email:
                company.email = c_email
                update_fields.append('email')
                activity += 'Changed company email to '+ str(c_email) +'.\n'
            company.save(update_fields=update_fields)
            history = models.History(
                user=emp,
                activity=activity,
                activity_type="edit company"
            )
            history.save()
            context_dict["message"] = 'Successfully updated company.'
            context_dict["success"] = True
        except Exception as e:
            context_dict["message"] = str(e)
            context_dict["success"] = False
            print(e)
    context_dict.update(context_helper.get_company_info(company))
    if context_dict.get('success', False):
        return HttpResponseRedirect('/view-companies')
    return render(
        request, "EditCompany.html", context_dict
    )


@login_required
def view_students(request):
    context_dict = {
        'title': 'All Students'
    }
    return render(
        request,
        'ViewStudent.html',
        context_dict
    )


@login_required
def view_company(request):
    context_dict = {
        'title': 'All Companies'
    }
    return render(
        request,
        'ViewCompany.html',
        context_dict
    )


@login_required
def delete_student(request, student_id):
    emp = models.Employee.objects.get(user=request.user)
    if not emp.student_permit:
        raise Http404
    student = models.Student.objects.filter(
        pk=student_id, soft_delete=False
    ).first()
    if not student:
        raise Http404
    student.soft_delete = True
    activity = 'Deleted student' + str(student) + '.\n'
    student.save(update_fields=['soft_delete'])
    history = models.History(
                user=emp,
                activity=activity,
                activity_type="delete student"
            )
    history.save()
    return HttpResponseRedirect('/view-students')


@login_required
def delete_company(request, company_id):
    emp = models.Employee.objects.get(user=request.user)
    if not emp.company_permit:
        raise Http404
    company = models.Company.objects.filter(
        pk=company_id, soft_delete=False
    ).first()
    if not company:
        raise Http404
    company.soft_delete = True
    activity = 'Deleted company' + str(company) + '.\n'
    company.save(update_fields=['soft_delete'])
    history = models.History(
                user=emp,
                activity=activity,
                activity_type="delete company"
            )
    history.save()
    return HttpResponseRedirect('/view-companies')



@login_required
def add_placement(request, student_id):
    # Try to fetch an Employee record for the current user.
    try:
        emp = models.Employee.objects.get(user=request.user)
    except models.Employee.DoesNotExist:
        emp = None

    if emp:
        # If the user is an employee, check for placement permission.
        if not emp.placement_permit:
            raise Http404("You do not have permission to add placements.")
        # Allow employee to add a placement for any student.
        student = models.Student.objects.filter(pk=student_id, soft_delete=False).first()
        if not student:
            raise Http404("Student not found.")
    else:
        # If no Employee record exists, assume the user is a student.
        # In this case, ensure they are editing their own record.
        student = models.Student.objects.filter(
            pk=student_id, soft_delete=False, user=request.user
        ).first()
        if not student:
            raise Http404("You are not allowed to add a placement for this student.")

    # Prepare additional context
    dyears = models.CampusDrive.objects.filter(soft_delete=False).values('drive_year').distinct()
    drive_years = [item['drive_year'] for item in dyears]
    context_dict = {
        "all_drives": context_helper.drives_info(),
        "dyears": drive_years,
        "student_id": student_id,
    }
    context_dict.update(context_helper.get_student_info(student))

    if request.method == 'POST':
        drive = request.POST.get('drive_picker')
        doj = request.POST.get('doj')
        if doj == "":
            doj = None

        # Check if placement already exists for this student & drive.
        try:
            campus_drive = models.CampusDrive.objects.get(pk=drive)
        except models.CampusDrive.DoesNotExist:
            context_dict["message"] = "Selected campus drive does not exist."
            context_dict["success"] = False
            return render(request, "AddPlacement.html", context_dict)

        duplicate_placement = models.Placements.objects.filter(
            student=student, campus_drive=campus_drive
        ).first()
        if duplicate_placement:
            context_dict["message"] = 'Placement already exists.'
            duplicate_placement.soft_delete = False
            duplicate_placement.save()
            return render(request, "AddPlacement.html", context_dict)

        try:
            placement = models.Placements(
                student=student,
                campus_drive=campus_drive,
                dateofjoining=doj,
            )
            placement.save()

            # Use the employee as history actor if available; otherwise, use the student.
            history_user = emp if emp is not None else student
            history = models.History(
                user=history_user,
                activity=f"Added placement for student ID {student_id}.",
                activity_type="add placement"
            )
            history.save()

            context_dict["message"] = 'Successfully added new placement.'
            context_dict["success"] = True
        except Exception as e:
            context_dict["message"] = str(e)
            context_dict["success"] = False
            print(e)

    return render(request, "AddPlacement.html", context_dict)


@login_required
def view_placement(request):
    context_dict = {
        'title': 'All Placements'
    }
    return render(
        request,
        'ViewPlacement.html',
        context_dict
    )


@login_required
def delete_placement(request, placements_id):
    emp = models.Employee.objects.get(user=request.user)
    if not emp.placement_permit:
        raise Http404
    placement = models.Placements.objects.filter(
        pk=placements_id, soft_delete=False
    ).first()
    if not placement:
        raise Http404
    placement.soft_delete = True
    activity = 'Deleted placement' + str(placement) + '.\n'
    placement.save(update_fields=['soft_delete'])
    history = models.History(
                user=emp,
                activity=activity,
                activity_type="delete placement"
            )
    history.save()
    return HttpResponseRedirect('/view-placements')


@login_required
def edit_placement(request, placements_id):
    emp = models.Employee.objects.get(user=request.user)
    if not emp.placement_permit:
        raise Http404
    placement = models.Placements.objects.filter(
        pk=placements_id, soft_delete=False
    ).first()
    if not placement:
        raise Http404
    context_dict = {
        'placements_id': placements_id,
        "all_drives": context_helper.drives_info()
    }
    if request.method == 'POST':
        update_fields = []
        activity = ''
        drive = request.POST.get('company_select')
        doj = request.POST.get('doj')
        if doj == "":
            doj = None
        try:
            if str(placement.campus_drive.pk) != str(drive):
                try:
                    old_drive = placement.campus_drive
                    placement.campus_drive = models.CampusDrive.objects.get(pk=drive)
                    placement.save()
                except Exception as e:
                    placement.soft_delete = True
                    placement.campus_drive = old_drive
                    placement.save()
                    placement = models.Placements.objects.filter(
                        soft_delete=True, student=placement.student,
                        campus_drive__pk=drive
                    ).first()
                    placement.soft_delete = False
                    placement.campus_drive = models.CampusDrive.objects.get(pk=drive)
                    placement.save(update_fields=['soft_delete', 'drive'])
                update_fields.append('drive')
                activity += 'Changed drive to ' + str(drive) + '.\n'
            if placement.dateofjoining != doj:
                placement.dateofjoining = doj
                update_fields.append('dateofjoining')
                activity += 'Changed date of joining to ' + str(doj) + '.\n'
            placement.save(update_fields=update_fields)
            history = models.History(
                user=emp,
                activity=activity,
                activity_type="edit placement"
            )
            history.save()
            context_dict["message"] = 'Successfully updated company.'
            context_dict["success"] = True
        except Exception as e:
            context_dict["message"] = str(e)
            context_dict["success"] = False
            print(e)
    context_dict.update(context_helper.get_placement_info(placement))
    for i in context_dict['drive']:
        try: del context_dict['all_drives'][i]
        except: pass
    if context_dict.get('success', False):
        return HttpResponseRedirect('/view-placements')
    return render(
        request, "editPlacement.html", context_dict
    )



@login_required
def add_campus_drive(request):
    context_dict = {}
    
    # Try to get the Employee record for the logged-in user.
    try:
        emp = models.Employee.objects.get(user=request.user)
    except models.Employee.DoesNotExist:
        # No employee record found, so this user is not authorized.
        raise Http404("Employee record not found. You are not authorized to add a campus drive.")
    
    # Check if the employee has the placement_permit.
    if not emp.placement_permit:
        raise Http404("You do not have permission to add a campus drive.")
    
    # Populate the context with the list of companies.
    context_dict["all_companies"] = context_helper.company_select()

    # Handle the form submission.
    if request.method == 'POST':
        company = request.POST.get('company_picker')
        drive_year = request.POST.get('driveyear')
        package = request.POST.get('package')
        bond_period = request.POST.get('bond')
        dateofdrive = request.POST.get('dateofdrive')
        
        # Check for duplicate campus drive.
        duplicate_drive = models.CampusDrive.objects.filter(
            company=models.Company.objects.get(pk=company), 
            package=package,
            drive_year=drive_year, 
            bond_period=bond_period,
        ).first()
        
        if duplicate_drive:
            context_dict["message"] = 'Campus Drive already exists.'
            duplicate_drive.soft_delete = False
            duplicate_drive.save()
            return render(request, "AddCampusDrive.html", context_dict)

        try:
            # Create and save the new CampusDrive record.
            drive = models.CampusDrive(
                company=models.Company.objects.get(pk=company),
                drive_year=drive_year,
                bond_period=bond_period,
                package=package,
                dateofdrive=dateofdrive,
            )
            drive.save()

            # Log the action in the history.
            history = models.History(
                user=emp,
                activity=f"Added drive for {str(drive.company)} for the year {str(drive_year)}.\n",
                activity_type="add campus drive"
            )
            history.save()
            
            context_dict["message"] = 'Successfully added new Campus Drive.'
            context_dict["success"] = True
        except Exception as e:
            context_dict["message"] = str(e)
            context_dict["success"] = False
            print(e)
    
    return render(request, "AddCampusDrive.html", context_dict)

@login_required
def edit_campus_drive(request, campusdrive_id):
    context_dict = {}
    emp = models.Employee.objects.get(user=request.user)
    if not emp.placement_permit:
        raise Http404
    drive = models.CampusDrive.objects.filter(
        pk=campusdrive_id, soft_delete=False
    ).first()
    if not drive:
        raise Http404
    context_dict = {
        'campusdrive_id': campusdrive_id,
        "all_companies": context_helper.company_select()
    }
    if request.method == 'POST':
        update_fields = []
        activity = ''
        company = request.POST.get('company_picker')
        drive_year = request.POST.get('driveyear')
        package = request.POST.get('package')
        bond_period = request.POST.get('bond')
        dateofdrive = request.POST.get('dateofdrive')
        try:
            if str(drive.company.pk) != str(company):
                try:
                    old_company = drive.company
                    drive.company = models.Company.objects.get(pk=company)
                    drive.save()
                except Exception as e:
                    drive.soft_delete = True
                    drive.company = old_company
                    drive.save()
                    drive = models.CampusDrive.objects.filter(
                        soft_delete=True, drive_year=drive.drive_year,
                        package=drive.package, bond_period=drive.bond_period, 
                        company__pk=company
                    ).first()
                    drive.soft_delete = False
                    drive.company = models.Company.objects.get(pk=company)
                    drive.save(update_fields=['soft_delete', 'company'])
                update_fields.append('company')
                activity += 'Changed company to ' + str(company) + '.\n'
            if drive.package != package:
                drive.package = package
                update_fields.append('package')
                activity += 'Changed name to '+ str(package) +'.\n'
            if drive.drive_year != drive_year:
                drive.drive_year = drive_year
                update_fields.append('drive_year')
                activity += 'Changed drive year to' + str(drive_year) + '.\n'
            if drive.bond_period != bond_period:
                drive.bond_period = bond_period
                update_fields.append('bond_period')
                activity += 'Changed bond period to' + str(bond_period) + '.\n'
            if drive.dateofdrive != dateofdrive:
                drive.dateofdrive = dateofdrive
                update_fields.append('dateofdrive')
                activity += 'Changed date of drive to' + str(dateofdrive) + '.\n'
            drive.save(update_fields=update_fields)
            history = models.History(
                user=emp,
                activity=activity,
                activity_type='Edit campus Drive'
            )
            history.save()
            context_dict["message"] = 'Successfully Edited Campus Drive.'
            context_dict["success"] = True
        except Exception as e:
            context_dict["message"] = str(e)
            context_dict["success"] = False
            print(e)
    context_dict.update(context_helper.get_drive_info(drive))
    for i in context_dict['company']:
        try: del context_dict['all_companies'][i]
        except: pass
    if context_dict.get('success', False):
        return HttpResponseRedirect('/view-drives')
    return render(
        request, "EditCampusDrive.html", context_dict
    )


@login_required
def view_campus_drive(request):
    context_dict = {
        'title': 'All Campus Drives'
    }
    return render(
        request,
        'ViewCampusDrive.html',
        context_dict
    )


@login_required
def delete_campus_drive(request, campusdrive_id):

    emp = models.Employee.objects.get(user=request.user)
    if not emp.placement_permit:
        raise Http404
    drive = models.CampusDrive.objects.filter(
        pk=campusdrive_id, soft_delete=False
    ).first()
    if not drive:
        raise Http404
    drive.soft_delete = True
    activity = 'Deleted Campus Drive' + str(drive) + '.\n'
    drive.save(update_fields=['soft_delete'])
    history = models.History(
                user=emp,
                activity=activity,
                activity_type="Deleted Campus Drive"
            )
    history.save()
    return HttpResponseRedirect('/view-drives')


def _search_result(request):
    context_dict = {}
    if request.method == 'GET':
        roll = request.GET.get('rollno')
    student = models.Student.objects.filter(
        soft_delete=False, roll_no=roll
    )
    student_serial = serializers.serialize('json', student)
    
    return JsonResponse(student_serial, safe=False)


def _search_result_(request):
    student = models.Student.objects.all().values(
        'name', 'dob', 'course', 'roll_no'
    ).filter(roll_no=611) 
    student_list = list(student)      
    return JsonResponse(student_list, safe=False)

def search(request):
    context_dict = {}
    if request.method == 'GET':
        roll = request.GET.get('roll')
    student = models.Student.objects.filter(
        soft_delete=False, roll_no=roll,
    ).first()
    if not student:
        raise Http404
    context_dict.update(context_helper.get_student_info(student))
    return render(request, "search.html", context_dict)

from django.shortcuts import render
from .models import Placements

def bar_chart(request):
    pname = (
        Placements.objects.filter(soft_delete=False)
        .values_list('campus_drive__company__name', flat=True)
        .distinct()  
    )
    
    packages = (
        Placements.objects.filter(soft_delete=False)
        .values_list('campus_drive__package', flat=True)
    )
    
    company_package_map = {}
    for company_name, package in zip(pname, packages):
        if company_name not in company_package_map:
            company_package_map[company_name] = []
        company_package_map[company_name].append(package)

    print(company_package_map)
    
    chart_data = []
    for company, package_list in company_package_map.items():
        package_count = {pkg: package_list.count(pkg) for pkg in set(package_list)}
        for pkg, count in package_count.items():
            chart_data.append({
                'company': company,
                'package': pkg,
                'count': count
            })
    
    context_dict = {
        'ylabel': 'Package Count',
        'datasets': [
            {
                'label': company,
                'dataset': [entry['count'] for entry in chart_data if entry['company'] == company]
            } for company in company_package_map.keys()
        ],
        'labels': [entry['package'] for entry in chart_data]
    }
    
    return render(request, "bcharts.html", context_dict)

import json

def pie_chart(request):
    pdata = models.Placements.objects.filter(
        soft_delete=False
    ).select_related('campus_drive__company').values_list('campus_drive__company__name', flat=True)

    ps = models.Placements.objects.filter(
        soft_delete=False
    ).values_list('student__id', flat=True)
    
    dataset = {}
    for i in range(len(pdata)):
        company_name = pdata[i]
        student_id = ps[i]
        if company_name not in dataset:
            dataset[company_name] = 0  
        dataset[company_name] += 1  

    chart_data = [{'name': key, 'y': value} for key, value in dataset.items()]

    chart_data_json = json.dumps(chart_data)

    context_dict = {
        'ylabel': 'Companies',
        'dataset': chart_data_json 
    }
    return render(request, "pcharts.html", context_dict)

def test_search(request):
    context_dict = {}
    param = request.GET.get('search_param')
    if param:
        results = models.Student.objects.filter(
            Q(roll_no__icontains=param)|Q(name__icontains=param)
        )[:20]
        context_dict['rows'] = results
    return render(request, 'test_search.html', context_dict)


def year_ajax(request):
    if request.method=="POST":
        print(request.POST)
        year = request.POST.get("year")
        companies = models.CampusDrive.objects.filter(drive_year=year).values(
            'company', 'company__name'
        ).distinct()
        if 'csrfmiddlewaretoken' not in request.POST:
            return render(request, 'foo.html', {'companies': companies})
    return render(request, 'year_ajax_test.html', {})