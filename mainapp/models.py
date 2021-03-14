from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
import jsonfield

class GeneralPractice(models.Model):
	name = models.CharField(max_length=32)
	registration_number = models.CharField(max_length=32)
	address = jsonfield.JSONField()
	contact_number = models.CharField(max_length=32)
	open_times = jsonfield.JSONField()

	class Meta:
		verbose_name_plural = "GeneralPractice"

	def __str__(self):
		return self.name

class Patient(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	date_of_birth = models.DateField() 
	address = jsonfield.JSONField()
	mobile = models.CharField(max_length=32)
	nhs_number = models.CharField(max_length=32)
	blood_group = models.CharField(max_length=32)
	patient_at = models.ForeignKey(GeneralPractice, on_delete=models.CASCADE)
	email_verified = models.BooleanField(default=False, blank=True)
	verification_data = jsonfield.JSONField()

	class Meta:
		verbose_name_plural = "Patient"

	def __str__(self):
		return self.user.get_full_name()

class Doctor(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	works_at = models.ForeignKey(GeneralPractice, on_delete=models.CASCADE)
	working_hours = jsonfield.JSONField()
	email_verified = models.BooleanField(default=False, blank=True)
	verification_data = jsonfield.JSONField()

	class Meta:
		verbose_name_plural = "Doctor"

class Nurse(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	works_at = models.ForeignKey(GeneralPractice, on_delete=models.CASCADE)
	working_hours = jsonfield.JSONField()
	email_verified = models.BooleanField(default=False, blank=True)
	verification_data = jsonfield.JSONField()

	class Meta:
		verbose_name_plural = "Nurse"

class Receptionist(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	works_at = models.ForeignKey(GeneralPractice, on_delete=models.CASCADE)
	working_hours = jsonfield.JSONField()
	email_verified = models.BooleanField(default=False, blank=True)
	verification_data = jsonfield.JSONField()

	class Meta:
		verbose_name_plural = "Receptionist"

class Appointments(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
	time = models.DateTimeField(null=True, blank=True)

	class Meta:
		verbose_name_plural = "Appointments"

class MyMedicalRecords(models.Model):
	# Used and done.
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	document = models.FileField(upload_to='myMedicalRecords/', blank=True, null=True,)

	class Meta:
		verbose_name_plural = "MyMedicalRecords"

class GPMedicalRecords(models.Model):
	# Used by staff to upload doc to the patient
	prescribed_to = models.ForeignKey(Patient, on_delete=models.CASCADE)
	prescribed_by = models.ForeignKey(Doctor, on_delete=models.CASCADE)
	document = models.FileField(upload_to='gpMedicalRecords/', blank=True, null=True,)
	access_to_patient = models.BooleanField(default=False)

	class Meta:
		verbose_name_plural = "GPMedicalRecords"

class GPCurrentMedication(models.Model):
	prescribed_to = models.ForeignKey(Patient, on_delete=models.CASCADE)
	prescribed_by = models.ForeignKey(Doctor, on_delete=models.CASCADE)
	name = models.CharField(max_length=32)
	description = models.TextField()
	start_date = models.DateField()
	prescribed_date = models.DateField(auto_now_add=True)

	class Meta:
		verbose_name_plural = "GPCurrentMedication"

class Notes(models.Model):
	# Used by the patients
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=32)
	description = models.TextField()
	date = models.DateTimeField(auto_now_add=True, blank=True)

	class Meta:
		verbose_name_plural = "Notes"

class MyCurrentMedication(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=32)
	description = models.TextField()
	start_date = models.DateField()

	class Meta:
		verbose_name_plural = "MyCurrentMedication"

class Countries(models.Model):
	alpha = models.CharField(max_length=4)
	name = models.CharField(max_length=64)

	class Meta:
		verbose_name_plural = "Countries"
		ordering = ('name',)

	def __str__ (self):
		return str(self.id) + " - " + self.alpha + " - " + self.name

class HealthAdvice(models.Model):
	title = models.CharField(max_length=64)
	fact = models.TextField()
	symptoms = models.TextField()

	class Meta:
		verbose_name_plural = "HealthAdvice"