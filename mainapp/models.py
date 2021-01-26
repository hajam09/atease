from django.db import models
from django.contrib.auth.models import User
import jsonfield
from datetime import datetime

class GeneralPractice(models.Model):
	name = models.CharField(max_length=32)
	accountNumber = models.IntegerField()
	address = jsonfield.JSONField()
	contactNumber = models.CharField(max_length=32)
	openTimes = jsonfield.JSONField()

class Patient(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	dateOfBirth = models.DateField() 
	address = jsonfield.JSONField()
	mobile = models.CharField(max_length=32)
	nhsNumber = models.CharField(max_length=32)
	bloodGroup = models.CharField(max_length=32)
	generalPractice = models.ForeignKey(GeneralPractice, on_delete=models.CASCADE)

class Doctor(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=32)
	generalPractice = models.ForeignKey(GeneralPractice, on_delete=models.CASCADE)
	workingHours = jsonfield.JSONField()

class Appointments(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
	time = models.DateTimeField(null=True, blank=True)

class MyMedicalRecords(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	document = models.FileField(upload_to='myMedicalRecords/', blank=True, null=True,)

class GPMedicalRecords(models.Model):
	generalPractice = models.ForeignKey(GeneralPractice, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	document = models.FileField(upload_to='gpMedicalRecords/', blank=True, null=True,)

class GPCurrentMedication(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
	name = models.CharField(max_length=32)
	descrption = models.TextField()
	startDate = models.DateField() 

class Notes(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=32)
	desciption = models.TextField()
	date = models.DateTimeField()

class MyCurrentMedication(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=32)
	desciption = models.TextField()
	startDate = models.DateField() 
	note = models.ForeignKey(Notes, on_delete=models.CASCADE)

class Countries(models.Model):
	alpha = models.CharField(max_length=4)
	name = models.CharField(max_length=64)

	class Meta:
		verbose_name_plural = "Countries"
		ordering = ('name',)

	def __str__ (self):
		return str(self.id) + " - " + self.alpha + " - " + self.name