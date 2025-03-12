from django.urls import path
from django.contrib.auth.decorators import login_required
from placement import  views
from placement import student_datatables_views
from placement import Company_Datatables_Views
from placement import Placement_Datatables_Views
from placement import drive_datatables_views

urlpatterns = [
 
    path('register/', views.register, name='register'),
    path('studlogin/', views.studlogin_view, name='studlogin'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('view-profile/', views.view_profile, name='view-profile'),
    path('stud_register/', views.Student_register, name='stud_register'),


    path('', views.index, name='index'),
    path('login/', views.login_view, name='login_view'),
    path('home/', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('add-student/', views.add_student, name='add_student'),
    path('edit-student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('view-students/', views.view_students, name='view_students'),
    path('view-students-dt/', login_required(student_datatables_views.StudentListDatatable.as_view()), name='view_students_dt'),
    path('add-company/', views.add_company, name='add_company'),
    path('edit-company/<int:company_id>/', views.edit_company, name='edit_company'),
    path('view-companies/', views.view_company, name='view_companies'),
    path('view-companies-dt/', login_required(Company_Datatables_Views.CompanyListDatatable.as_view()), name='view_companies_dt'),
    path('delete-company/<int:company_id>/', views.delete_company, name='delete_company'),
    path('add-placement/<int:student_id>/', views.add_placement, name='add_placement'),
    path('view-placements/', views.view_placement, name='view_placements'),
    path('view-placements-dt/', login_required(Placement_Datatables_Views.PlacementListDatatable.as_view()), name='view_placements_dt'),
    path('delete-placement/<int:placements_id>/', views.delete_placement, name='delete_placement'),
    path('edit-placement/<int:placements_id>/', views.edit_placement, name='edit_placement'),
    path('bcharts/', views.bar_chart, name='bcharts'),
    path('pcharts/', views.pie_chart, name='pcharts'),
    path('cpassword/', views.change_password, name='cpassword'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('reset-password/<uidb64>/<token>/', views.password_resetenter, name='password_resetenter'),
    path('test-search/', views.test_search, name='test_search'),
    path('add-drive/', views.add_campus_drive, name='add_drive'),
    path('edit-drive/<int:campusdrive_id>/', views.edit_campus_drive, name='edit_drive'),
    path('view-drives/', views.view_campus_drive, name='view_drives'),
    path('view-drive-dt/', login_required(drive_datatables_views.DriveListDatatable.as_view()), name='view_drive_dt'),
    path('delete-drigve/<int:campusdrive_id>/', views.delete_campus_drive, name='delete_drive'),
    path('year-ajax/', views.year_ajax, name='year_ajax'),
    path('my-page/', views.mypage, name='my_page'),
]