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

class TestViewCreateProfile(TestCase):

	def setUp(self):
		self.client = Client()
		self.url = reverse('mainapp:create_profile')
		install_gp()
		install_countries()
		self.user_1 = User.objects.create_user(username="randomuser", password='A1b2C3d4E5f6G7h')
		self.user_1.save()
		self.client.login(username=self.user_1.username, password='A1b2C3d4E5f6G7h')

	def test_patient_profile_view_GET(self):
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "mainapp/create_profile.html")

	def test_patient_profile_already_exists(self):
		Patient.objects.create( user=self.user_1, date_of_birth="2020-01-01", patient_at=GeneralPractice.objects.order_by("?").first() )
		context = {

		}
		response = self.client.post(self.url, context)
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/profile/patient/')

	def test_doctor_profile_already_exists(self):
		Doctor.objects.create( user=self.user_1, works_at = GeneralPractice.objects.order_by("?").first(), working_hours = {} )
		context = {

		}
		response = self.client.post(self.url, context)
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/profile/doctor/')

	def test_nurse_profile_already_exists(self):
		Nurse.objects.create( user=self.user_1, works_at = GeneralPractice.objects.order_by("?").first(), working_hours = {} )
		context = {

		}
		response = self.client.post(self.url, context)
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/profile/nurse/')

	def test_receptionist_profile_already_exists(self):
		Receptionist.objects.create( user=self.user_1, works_at = GeneralPractice.objects.order_by("?").first(), working_hours = {} )
		context = {

		}
		response = self.client.post(self.url, context)
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/profile/receptionist/')

	def test_create_new_patient_profile(self):
		fake = Faker()

		alphabet = list(string.ascii_uppercase)
		postalZip = random.choice(alphabet) + random.choice(alphabet) + str(randint(1, 100)) + " " + str(randint(1, 10)) + random.choice(alphabet) + random.choice(alphabet)

		context = {
			"patient_profile": "",
			"date_of_birth": "2020-01-01",
			"mobile_number": "+44"+str(randint(7000000000, 7999999999)),
			"nhs_number": str(randint(70000000, 79999999)),
			"blood_group": random.choice(['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']),
			"list_of_gps": GeneralPractice.objects.order_by("?").first().id,
			"country": "GB",
			"address_1": str(randint(1, 100)) + " " + fake.unique.first_name() + " " + "Road",
			"address_2": fake.unique.last_name(),
			"city": "London",
			"stateProvince": "Essex",
			"postalZip": postalZip
		}

		patient_profile_count = Patient.objects.count()

		response = self.client.post(self.url, context)
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/profile/patient/')
		self.assertEqual(patient_profile_count+1, Patient.objects.count())

	def test_create_new_staff_doctor_profile(self):
		working_hours = {
			"monday_from": "09:00",
			"monday_to": "18:00",
			"tuesday_from": "09:00",
			"tuesday_to": "18:00",
			"wednesday_from": "09:00",
			"wednesday_to": "18:00",
			"thursday_from": "09:00",
			"thursday_to": "18:00",
			"friday_from": "09:00",
			"friday_to": "18:00",
		}
		context = {
			"staff_profile": "",
			"role": "doctor",
			"list_of_gps": GeneralPractice.objects.order_by("?").first().id,
		}

		context.update(working_hours)

		doctor_profile_count = Doctor.objects.count()

		response = self.client.post(self.url, context)
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/profile/doctor/')
		self.assertEqual(doctor_profile_count+1, Doctor.objects.count())

	def test_create_new_staff_nurse_profile(self):
		working_hours = {
			"monday_from": "09:00",
			"monday_to": "18:00",
			"tuesday_from": "09:00",
			"tuesday_to": "18:00",
			"wednesday_from": "09:00",
			"wednesday_to": "18:00",
			"thursday_from": "09:00",
			"thursday_to": "18:00",
			"friday_from": "09:00",
			"friday_to": "18:00",
		}
		context = {
			"staff_profile": "",
			"role": "nurse",
			"list_of_gps": GeneralPractice.objects.order_by("?").first().id,
		}

		context.update(working_hours)

		nurse_profile_count = Nurse.objects.count()

		response = self.client.post(self.url, context)
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/profile/nurse/')
		self.assertEqual(nurse_profile_count+1, Nurse.objects.count())

	def test_create_new_staff_receptionist_profile(self):
		working_hours = {
			"monday_from": "09:00",
			"monday_to": "18:00",
			"tuesday_from": "09:00",
			"tuesday_to": "18:00",
			"wednesday_from": "09:00",
			"wednesday_to": "18:00",
			"thursday_from": "09:00",
			"thursday_to": "18:00",
			"friday_from": "09:00",
			"friday_to": "18:00",
		}
		context = {
			"staff_profile": "",
			"role": "receptionist",
			"list_of_gps": GeneralPractice.objects.order_by("?").first().id,
		}

		context.update(working_hours)

		receptionist_profile_count = Receptionist.objects.count()

		response = self.client.post(self.url, context)
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/profile/receptionist/')
		self.assertEqual(receptionist_profile_count+1, Receptionist.objects.count())