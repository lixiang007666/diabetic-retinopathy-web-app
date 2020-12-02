from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from .models import Profile, Patients
from django.contrib.auth.models import User
from .forms import (DoctorRegisterForm,
                    DoctorUpdateForm,
                    ProfileUpdateForm)
from django.contrib.auth.decorators import login_required
import string
import random
from PIL import Image
from io import BytesIO
import tensorflow as tf
from pathlib import Path
import json
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

# Importing custom codes for predictions
from doctors.predictions.predict_ma import predict_ma
from doctors.predictions.predict_he import predict_he
from doctors.predictions.predict_hx import predict_hx
from doctors.predictions.predict_se import predict_se
from doctors.predictions.predict_od import predict_od
from doctors.predictions.predict_vessels import predict_vessels
from doctors.predictions.dr_dme_grade import dr_dme_grade
# from doctors.predictions.dr_dme_grade import dme_grade

# Class based views
from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView,
                                  DeleteView)
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        UserPassesTestMixin)
from django.http import HttpResponse


# Create your views here.
def findDoctor(request):
    context = {
        'doctors': User.objects.all()
    }
    return render(request, 'doctors/find_doctor.html')


class DoctorListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'doctors/find_doctor.html'
    context_object_name = 'doctors'
    ordering = ['first_name']
    paginate_by = 5
    # <app>/<model>_<viewtype>.html


class DoctorDetailView(LoginRequiredMixin,
                       DetailView):
    model = User
    context_object_name = 'doctors'
    template_name = 'doctors/doctor_profile_detail.html'


class PatientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Patients
    success_url = '/profile'

    def test_func(self):
        patients = self.get_object()
        if self.request.user == patients.doctor_name:
            return True
        return False


class PatientCreateView(LoginRequiredMixin, CreateView):
    model = Patients
    # success_url = '/profile'

    fields = ['first_name', 'last_name', 'age',
              'sex', 'identity_number', 'patient_address']

    # Generating random letters and passing default value

    def randomStringDigits(self, stringLength = 10):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(stringLength))

    def form_valid(self, form):
        form.instance.diagnosis_id = self.randomStringDigits(10)
        form.instance.doctor_name = self.request.user
        return super().form_valid(form)


def dashboard(request):
    return render(request, 'doctors/dashboard.html')


def doctorRegister(request):
    if request.method == 'POST':
        form = DoctorRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'{username}, Your account has been created, Log In!')
            return redirect('doctor-login')
    else:
        form = DoctorRegisterForm()

    return render(request, 'doctors/doctor_register.html', {'form':form})


def about(request):
    return render(request, 'doctors/about.html')


@login_required()
def afterLoginDashboard(request):
    return render(request, 'doctors/after_login_dashboard.html')


@login_required()
def doctorProfile(request):
    context = {
        'patients': Patients.objects.filter(doctor_name = request.user)
    }

    return render(request, 'doctors/doctor_profile.html', context)


@login_required()
def doctorProfileUpdate(request):
    if request.method == 'POST':
        d_form = DoctorUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)

        if d_form.is_valid() and p_form.is_valid():
            d_form.save()
            p_form.save()
            return redirect('doctor-profile')
    else:
        d_form = DoctorUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)


    context = {
        'd_form': d_form,
        'p_form': p_form
    }

    return render(request, 'doctors/doctor_profile_update.html', context)


@login_required()
def dr_dme_grading(request):
    template_name = 'doctors/dr_grade_analysis.html'
    if request.method == 'POST':
        if request.POST.get("upload_img"):
            image_files = request.FILES.getlist('browse_img')
            if not image_files:
                context = {
                    'status':'no-image'
                }
                return render(request, template_name, context)
            images = []
            for img in image_files:
                image = Image.open(BytesIO(img.read()))
                images.append(image)
            for file in os.listdir("media/dr_dme_grading/"):
                os.remove("media/dr_dme_grading/" + file)
            images[0].save("media/dr_dme_grading/grade_dr.jpg", "JPEG", quality=100)

            context = {
                'status': "uploaded",
                'predict': "false"
            }
            return render(request, template_name, context)

        elif request.POST.get("predict_img"):
            my_file = Path("media/dr_dme_grading/grade_dr.jpg")
            if my_file.is_file():
                input_image = Image.open("media/dr_dme_grading/grade_dr.jpg")
            else:
                context = {
                    'status': "no-image"
                }
                return render(request, template_name, context)
            predictions = dr_dme_grade(input_image)
            predictions = 100*predictions
            grade = np.argmax(predictions[0])

            # Changed here
            # predictions1 = dme_grade(input_image)
            # predictions1 = 100*predictions1
            # grade1 = np.argmax(predictions1[0])


            context = {
                'status': "uploaded",
                'predict': "true",
                'predictions': predictions[0],
                'grade': grade
            }
            return render(request, template_name, context)

    return render(request, template_name)


@login_required()
def vessels_segment(request):
    template_name = 'doctors/blood_vessels_segmentation.html'
    if request.method == 'POST':
        if request.POST.get("upload_vessels"):
            image_files = request.FILES.getlist('browse_vessels')
            if not image_files:
                context = {
                    'status': "no-image"
                }
                return render(request, template_name, context)
            images = []
            for img in image_files:
                img_name = img.name
                image = Image.open(BytesIO(img.read()))
                images.append(image)
            for file in os.listdir("media/blood_vessels/"):
                os.remove("media/blood_vessels/" + file)
            images[0].save("media/blood_vessels/predict_vessels.jpg", "JPEG", quality=100)

            context = {
                'status': "uploaded",
                'predict': "false"
            }
            return render(request, template_name, context)

        elif request.POST.get("predict_vessels"):
            my_file = Path("media/blood_vessels/predict_vessels.jpg")
            if my_file.is_file():
                input_image = Image.open("media/blood_vessels/predict_vessels.jpg")
            else:
                context = {
                    'status': "no-image"
                }
                return render(request, template_name, context)
            predicted_image = predict_vessels(input_image)
            # predicted_image.save("media/blood_vessels/predicted_vessels.jpg", "JPEG", quality=100)
            plt.imsave("media/blood_vessels/predicted_vessels.jpg", predicted_image)
            context = {
                'status': "uploaded",
                'predict': "true"
            }
            return render(request, template_name, context)

    return render(request, template_name)


@login_required()
def optic_disc(request):
    template_name = 'doctors/optic_disc.html'
    if request.method == 'POST':
        if request.POST.get("upload_od"):
            image_files = request.FILES.getlist('browse_od')
            if not image_files:
                context = {
                    'status': "no-image"
                }
                return render(request, template_name, context)
            images = []
            for img in image_files:
                img_name = img.name
                image = Image.open(BytesIO(img.read()))
                images.append(image)
            for file in os.listdir("media/optic_disc/"):
                os.remove("media/optic_disc/" + file)
            images[0].save("media/optic_disc/predict_od.jpg", "JPEG", quality=100)

            context = {
                'status': "uploaded",
                'predict': "false"
            }
            return render(request, template_name, context)

        elif request.POST.get("predict_od"):
            my_file = Path("media/optic_disc/predict_od.jpg")
            if my_file.is_file():
                input_image = tf.read_file("media/optic_disc/predict_od.jpg")
            else:
                context = {
                    'status': "no-image"
                }
                return render(request, template_name, context)
            predicted_image = predict_od(input_image)
            predicted_image.save("media/optic_disc/predicted_od.jpg", "JPEG", quality=100)
            context = {
                'status': "uploaded",
                'predict': "true"
            }
            return render(request, template_name, context)

    return render(request, template_name)


@login_required()
def lesion_he(request):
    template_name = 'doctors/lesion_he.html'
    if request.method == 'POST':
        if request.POST.get("upload_he"):
            image_files = request.FILES.getlist('browse_he')
            if not image_files:
                context = {
                    'status': "no-image"
                }
                return render(request, template_name, context)
            images = []
            for img in image_files:
                img_name = img.name
                image = Image.open(BytesIO(img.read()))
                images.append(image)
            for file in os.listdir("media/haemorrhage/"):
                os.remove("media/haemorrhage/" + file)
            images[0].save("media/haemorrhage/predict_he.jpg", "JPEG", quality=100)

            context = {
                'status': "uploaded",
                'predict': "false"
            }
            return render(request, template_name, context)

        elif request.POST.get("predict_he"):
            my_file = Path("media/haemorrhage/predict_he.jpg")
            if my_file.is_file():
                input_image = tf.read_file("media/haemorrhage/predict_he.jpg")
            else:
                context = {
                    'status': "no-image"
                }
                return render(request, template_name, context)
            predicted_image = predict_he(input_image)
            predicted_image.save("media/haemorrhage/predicted_he.jpg", "JPEG", quality=100)
            context = {
                'status': "uploaded",
                'predict': "true"
            }
            return render(request, template_name, context)

    return render(request, template_name)


@login_required()
def lesion_hx(request):
    template_name = 'doctors/lesion_hx.html'
    if request.method == 'POST':
        if request.POST.get("upload_hx"):
            image_files = request.FILES.getlist('browse_hx')
            if not image_files:
                context = {
                    'status': "no-image"
                }
                return render(request, template_name, context)
            images = []
            for img in image_files:
                img_name = img.name
                image = Image.open(BytesIO(img.read()))
                images.append(image)
            for file in os.listdir("media/hard_exudates/"):
                os.remove("media/hard_exudates/" + file)
            images[0].save("media/hard_exudates/predict_hx.jpg", "JPEG", quality=100)

            context = {
                'status': "uploaded",
                'predict': "false"
            }
            return render(request, template_name, context)
        elif request.POST.get("predict_hx"):
            my_file = Path("media/hard_exudates/predict_hx.jpg")
            if my_file.is_file():
                input_image = tf.read_file("media/hard_exudates/predict_hx.jpg")
            else:
                context = {
                    'status': "no-image"
                }
                return render(request, template_name, context)
            predicted_image = predict_hx(input_image)
            predicted_image.save("media/hard_exudates/predicted_hx.jpg", "JPEG", quality=100)
            context = {
                'status': "uploaded",
                'predict': "true"
            }
            return render(request, template_name, context)

    return render(request, template_name)

@login_required()
def lesion_se(request):
    template_name = 'doctors/lesion_se.html'
    if request.method == 'POST':
        if request.POST.get("upload_se"):
            image_files = request.FILES.getlist('browse_se')
            if not image_files:
                context = {
                    'status': "no-image"
                }
                return render(request, template_name, context)
            images = []
            for img in image_files:
                img_name = img.name
                image = Image.open(BytesIO(img.read()))
                images.append(image)
            for file in os.listdir("media/soft_exudates/"):
                os.remove("media/soft_exudates/" + file)
            images[0].save("media/soft_exudates/predict_se.jpg", "JPEG", quality=100)

            context = {
                'status': "uploaded",
                'predict': "false"
            }
            return render(request, template_name, context)
        elif request.POST.get("predict_se"):
            my_file = Path("media/soft_exudates/predict_se.jpg")
            if my_file.is_file():
                input_image = tf.read_file("media/soft_exudates/predict_se.jpg")
            else:
                context = {
                    'status': "no-image"
                }
                return render(request, template_name, context)
            predicted_image = predict_se(input_image)
            predicted_image.save("media/soft_exudates/predicted_se.jpg", "JPEG", quality=100)
            context = {
                'status': "uploaded",
                'predict': "true"
            }
            return render(request, template_name, context)

    return render(request, template_name)


@login_required()
def lesionsPrediction(request):
    template_name = 'doctors/lesions_segmentation.html'
    if request.method == 'POST':
        if request.POST.get("upload_ma"):
            image_files = request.FILES.getlist('browse_ma')
            if not image_files:
                context = {
                    'status' : "no-image"
                }
                return render(request, template_name, context)
            images = []
            for img in image_files:
                img_name = img.name
                image = Image.open(BytesIO(img.read()))
                images.append(image)
            for file in os.listdir("media/microaneurysms/"):
                os.remove("media/microaneurysms/"+file)
            images[0].save("media/microaneurysms/predict_ma.jpg", "JPEG", quality = 100)

            context = {
                'status' : "uploaded",
                'predict' : "false"
            }
            return render(request, template_name, context)
        elif request.POST.get("predict_ma"):
            my_file = Path("media/microaneurysms/predict_ma.jpg")
            if my_file.is_file():
                input_image = tf.read_file("media/microaneurysms/predict_ma.jpg")
            else:
                context = {
                    'status':"no-image"
                }
                return render(request, template_name, context)
            predicted_image = predict_ma(input_image)
            predicted_image.save("media/microaneurysms/predicted_ma.jpg", "JPEG", quality = 100)
            context = {
                'status': "uploaded",
                'predict': "true"
            }
            return render(request, template_name, context)

    return render(request, template_name)



