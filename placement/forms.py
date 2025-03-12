from django import forms
from placement.tasks import celery_test_task

class AddForm(forms.Form):
    num2 = forms.IntegerField(label="num2")
    num1 = forms.IntegerField(label="num1")
    def save(self):
        celery_test_task.delay(
            self.cleaned_data['num1'], self.cleaned_data['num2'])

from django import forms
from django.contrib.auth.models import User
from .models import Student

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

    class Meta:
        model = Student
        fields = ['name', 'email', 'roll_no', 'gender', 'dob', 'phone', 'curr_address',
                  'perm_address', 'blood_group', 'guardian_name', 'guardian_type',
                  'guardian_phone', 'course', 'batch']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data
    
class LoginForm(forms.Form):
    Email = forms.EmailField( max_length=100)
    Password = forms.CharField(widget=forms.PasswordInput(), )
