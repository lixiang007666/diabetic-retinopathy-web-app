from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.urls import reverse

# Create your models here.
# Inherits from models.Model


class Patients(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    age = models.IntegerField()
    sex_type = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Others')
    ]
    sex = models.CharField(
        max_length=10,
        choices= sex_type,
        default= 'M'
    )
    identity_number = models.CharField(max_length=15)
    patient_address = models.CharField(max_length=50)
    diagnosis_id = models.CharField(max_length=10)
    doctor_name = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.first_name

    def get_absolute_url(selfS):
        return reverse('doctor-profile')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    doctor_type = models.CharField(max_length=30)
    mc_number = models.CharField(max_length= 10)
    doctor_address = models.CharField(max_length=100)
    doctor_contact = models.CharField(max_length=20)
    image = models.ImageField(default='default.jpg', upload_to='doctor-profiles')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        img = Image.open(self.image.path)
        if img.height > 500 or img.width > 500:
            output_size = (400, 400)
            img.thumbnail(output_size)
            img.save(self.image.path)
