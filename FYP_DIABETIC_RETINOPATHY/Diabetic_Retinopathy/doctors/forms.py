from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class DoctorRegisterForm(UserCreationForm):
    first_name = forms.CharField(required=True, max_length=20)
    last_name = forms.CharField(required=True, max_length=20)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class DoctorUpdateForm(forms.ModelForm):
    first_name = forms.CharField(required=True, max_length=20)
    last_name = forms.CharField(required=True, max_length=20)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


# required field changed
class ProfileUpdateForm(forms.ModelForm):
    doctor_type = forms.CharField(max_length=30)
    mc_number = forms.CharField(max_length=10)
    doctor_address = forms.CharField(max_length=100)
    doctor_contact = forms.CharField(max_length=20)

    class Meta:
        model = Profile
        fields = ['doctor_type', 'mc_number', 'doctor_address', 'doctor_contact', 'image']
