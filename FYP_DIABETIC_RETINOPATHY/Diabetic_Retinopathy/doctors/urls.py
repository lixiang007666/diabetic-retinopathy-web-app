from django.urls import path
from . import views
from doctors import views as doctor_views
from .views import (DoctorListView,
                    DoctorDetailView,
                    PatientCreateView,
                    PatientDeleteView)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.doctorRegister, name='doctor-register'),
    path('profile/', views.doctorProfile, name='doctor-profile'),
    path('update/', views.doctorProfileUpdate, name='doctor-profile-update'),
    path('welcome/', views.afterLoginDashboard, name='after-login-dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='doctors/doctor_login.html'), name = 'doctor-login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='doctors/doctor_logout.html'), name = 'doctor-logout'),
    path('', views.dashboard, name='doctor-home'),
    path('patients-create/', PatientCreateView.as_view(), name='patients-create'),
    path('patients/<int:pk>/delete/', PatientDeleteView.as_view(), name='patient-delete'),

    path('find-doctor/', DoctorListView.as_view(), name='find-doctor'),
    path('find-doctor/<int:pk>/', DoctorDetailView.as_view(), name='profile-detail'),

    # Image uploading and predicting paths testing
    path('lesions-segmentation/', doctor_views.lesionsPrediction, name='lesions-prediction'),
    path('lesion-he/', doctor_views.lesion_he, name='lesion-he'),
    path('lesion-hx/', doctor_views.lesion_hx, name='lesion-hx'),
    path('lesion-se/', doctor_views.lesion_se, name='lesion-se'),
    path('vessels-segment/', doctor_views.vessels_segment, name='vessels-segment'),
    path('optic-dics/', doctor_views.optic_disc, name='optic-disc'),

    # DR and DME Grading template path
    path('image-grading/', doctor_views.dr_dme_grading, name='image-grading'),
]