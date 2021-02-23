from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from mainapp.utils import install_patients, install_gp, install_countries
from unittest import skip
from mainapp.models import Countries, Patient, Notes, MyCurrentMedication

# coverage run --source=mainapp manage.py test mainapp
# coverage html

@skip("")
class TestViewPatientProfile(TestCase):

	def setUp(self):
		self.client = Client()
		self.url = reverse('mainapp:patient_profile')
		install_gp()
		install_patients()
		install_countries()
		self.user_1 = User.objects.order_by("?").first()
		self.client.login(username=self.user_1.email, password='A1b2C3d4E5f6G7h')

	def test_patient_profile_GET(self):
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "mainapp/patient_profile.html")

	def test_patient_profile_update_patient_profile(self):
		context = {
			"UPDATEPATIENTPROFILE": "",
			"first_name": "newfirstname",
			"last_name": "newlastname",
			"email": self.user_1.email,
			"mobile": "+447123456789"
		}
		response = self.client.post(self.url, context)
		self.assertEquals(response.status_code, 302)
		self.assertRedirects(response, '/profile/patient/')

		updated_patient_profile = Patient.objects.get(user=self.user_1)
		self.assertEquals(updated_patient_profile.user.first_name, 'newfirstname')
		self.assertEquals(updated_patient_profile.user.last_name, 'newlastname')
		self.assertEquals(updated_patient_profile.mobile, '+447123456789')

	def test_patient_profile_update_patient_address(self):
		country = Countries.objects.get(alpha="GB")

		context = {
			"UPDATEPATIENTADDRESS": "",
			"country": "GB",
			"address_1": "204 Eversholt Road",
			"address_2": "Euston",
			"city": "London",
			"stateProvince": "Essex",
			"postalZip": "YM5 2DG"
		}

		response = self.client.post(self.url, context)
		updated_patient_profile = Patient.objects.get(user=self.user_1)
		new_location = {
			"address_1": context["address_1"],
			"address_2": context["address_2"],
			"city": context["city"],
			"stateProvince": context["stateProvince"],
			"postalZip": context["postalZip"],
			"country": {"alpha": country.alpha, "name": country.name}
		}
		self.assertEqual(updated_patient_profile.address, new_location)
		self.assertEquals(response.status_code, 302)
		self.assertRedirects(response, '/profile/patient/')

	def test_patient_profile_create_notes(self):
		context = {
			"CREATENOTES": "",
			"title": "notes title",
			"description": "notes description"
		}
		notes_count = Notes.objects.count()
		response = self.client.post(self.url, context)
		self.assertEquals(response.status_code, 302)
		self.assertRedirects(response, '/profile/patient/')
		self.assertEquals(Notes.objects.count(), (notes_count+1))

	def test_patient_profile_create_my_current_medication(self):
		context = {
			"Create_My_Current_Medication": "",
			"name": "medication title",
			"description": "medication description",
			"start_date": "2020-01-01"
		}
		medication_count = MyCurrentMedication.objects.count()
		response = self.client.post(self.url, context)
		self.assertEquals(response.status_code, 302)
		self.assertRedirects(response, '/profile/patient/')
		self.assertEquals(MyCurrentMedication.objects.count(), (medication_count+1))

	def test_patient_profile_delete_notes(self):
		new_note = Notes.objects.create( user = self.user_1, title = "notes title", description = "notes description" )
		context = {
			"DELETENOTES": "",
			"notes_id": new_note.id,
		}

		notes_count = Notes.objects.count()
		response = self.client.post(self.url, context)
		self.assertEquals(response.status_code, 302)
		self.assertRedirects(response, '/profile/patient/')
		self.assertEquals(Notes.objects.count(), (notes_count-1))
		self.assertFalse(Notes.objects.filter(id=new_note.id).exists())

	def test_patient_profile_delete_my_medication(self):
		new_med = MyCurrentMedication.objects.create( user = self.user_1, name = 'med name', description = 'med description', start_date = '2020-01-01' )
		context = {
			"DELETE_my_medication": "",
			"my_medication_id": new_med.id,
		}

		medication_count = MyCurrentMedication.objects.count()
		response = self.client.post(self.url, context)
		self.assertEquals(response.status_code, 302)
		self.assertRedirects(response, '/profile/patient/')
		self.assertEquals(MyCurrentMedication.objects.count(), (medication_count-1))
		self.assertFalse(MyCurrentMedication.objects.filter(id=new_med.id).exists())