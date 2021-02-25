from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from mainapp.utils import install_patients, install_gp, install_countries
from unittest import skip
from mainapp.models import *
from random import randint
from faker import Faker
import string, random

# coverage run --source=mainapp manage.py test mainapp
# coverage html

@skip("")
class TestViewGPView(TestCase):

	def setUp(self):
		self.client = Client()
		self.url = reverse('mainapp:gp_view')
		install_gp()
		install_patients()
		self.user_doctor = User.objects.create_user(username="doctoruser", password='A1b2C3d4E5f6G7h')
		self.user_doctor.save()
		self.user_nurse = User.objects.create_user(username="nurseuser", password='A1b2C3d4E5f6G7h')
		self.user_nurse.save()
		self.user_receptionist = User.objects.create_user(username="receptionistuser", password='A1b2C3d4E5f6G7h')
		self.user_receptionist.save()
		self.doc_obj = Doctor.objects.create( user=self.user_doctor, works_at = GeneralPractice.objects.order_by("?").first(), working_hours = {} )
		self.nurse_obj = Nurse.objects.create( user=self.user_nurse, works_at = GeneralPractice.objects.order_by("?").first(), working_hours = {} )
		self.receptionist_obj = Receptionist.objects.create( user=self.user_receptionist, works_at = GeneralPractice.objects.order_by("?").first(), working_hours = {} )

	def test_user_doctor_templates_get(self):
		self.client.login(username='doctoruser', password='A1b2C3d4E5f6G7h')
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "mainapp/gp_view.html")
		self.assertEquals(response.context["can_edit_opening_times"], False)
		self.assertEquals(response.context["profile"], self.doc_obj)

	def test_user_nurse_templates_get(self):
		self.client.login(username='nurseuser', password='A1b2C3d4E5f6G7h')
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "mainapp/gp_view.html")
		self.assertEquals(response.context["can_edit_opening_times"], False)
		self.assertEquals(response.context["profile"], self.nurse_obj)

	def test_user_receptionist_templates_get(self):
		self.client.login(username='receptionistuser', password='A1b2C3d4E5f6G7h')
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "mainapp/gp_view.html")
		self.assertEquals(response.context["can_edit_opening_times"], True)
		self.assertEquals(response.context["profile"], self.receptionist_obj)

	def test_receptionist_update_GP_hours(self):
		self.client.login(username='receptionistuser', password='A1b2C3d4E5f6G7h')
		open_times = {
			"monday": {
				"from": "09:30",
				"to": "18:00"
			},
			"tuesday": {
				"from": "09:30",
				"to": "18:00"
			},
			"wednesday": {
				"from": "09:30",
				"to": "18:00"
			},
			"monday": {
				"from": "09:30",
				"to": "18:00"
			},
			"thursday": {
				"from": "09:30",
				"to": "18:00"
			},
			"friday": {
				"from": "09:30",
				"to": "18:00"
			}
		}
		new_opening_hours = {
			"monday_from": "09:30",
			"monday_to": "18:00",
			"tuesday_from": "09:30",
			"tuesday_to": "18:00",
			"wednesday_from": "09:30",
			"wednesday_to": "18:00",
			"thursday_from": "09:30",
			"thursday_to": "18:00",
			"friday_from": "09:30",
			"friday_to": "18:00",
		}
		context = {
			"Update_GP_Hours": "",
		}
		context.update(new_opening_hours)

		response = self.client.post(self.url, context)
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/gp_view/')
		self.assertEqual(Receptionist.objects.get(user=User.objects.get(username='receptionistuser')).works_at.open_times, open_times)

	def test_staff_search_for_patients_first_name_only(self):
		self.client.login(username='doctoruser', password='A1b2C3d4E5f6G7h')
		context = {
			"search_for_patients": "",
			"patient_name": ""
		}
		patients_of_this_gp = Patient.objects.filter(patient_at=self.doc_obj.works_at, user__first_name__icontains="") | Patient.objects.filter(patient_at=self.doc_obj.works_at, user__last_name__icontains="") 
		response = self.client.post(self.url, context)
		self.assertEquals(response.context["patients"].count(), patients_of_this_gp.count())

	def test_staff_search_for_patients_full_name(self):
		random_patient = Patient.objects.order_by("?").first()
		self.client.login(username='doctoruser', password='A1b2C3d4E5f6G7h')
		context = {
			"search_for_patients": "",
			"patient_name": random_patient.user.get_full_name()
		}
		patients_of_this_gp = Patient.objects.filter(patient_at=self.doc_obj.works_at, user__first_name__icontains=random_patient.user.first_name) | Patient.objects.filter(patient_at=self.doc_obj.works_at, user__last_name__icontains=random_patient.user.last_name) 
		response = self.client.post(self.url, context)
		self.assertEquals(response.context["patients"].count(), patients_of_this_gp.count())