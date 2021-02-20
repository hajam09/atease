from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from mainapp.utils import install_patients, install_gp
from unittest import skip

# coverage run --source=mainapp manage.py test mainapp
# coverage html

@skip("")
class TestViewSignUp(TestCase):

	def setUp(self):
		self.client = Client()
		self.url = reverse('mainapp:signup')
		install_gp()
		install_patients()
		self.user_1 = User.objects.order_by("?").first()

	def test_signup_GET(self):
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "mainapp/signup.html")

	def test_signup_user_already_exists(self):
		context = {
			"SIGNUP": "",
			"first_name": "firstname",
			"last_name": "lastname",
			"email": self.user_1.email,
			"password": "PassWord123@"
		}
		response = self.client.post(self.url, context)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.context["message"], "An account already exists for this email address!")
		self.assertEquals(response.context["email"], self.user_1.email)
		self.assertEquals(response.context["firstname"], "firstname")
		self.assertEquals(response.context["lastname"], "lastname")
		self.assertTemplateUsed(response, "mainapp/signup.html")

	def test_signup_user_weak_password(self):
		context = {
			"SIGNUP": "",
			"first_name": "firstname",
			"last_name": "lastname",
			"email": "newemail@email.com",
			"password": "123"
		}
		response = self.client.post(self.url, context)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.context["message"], "Your password is not strong enough.")
		self.assertEquals(response.context["email"], "newemail@email.com")
		self.assertEquals(response.context["firstname"], "firstname")
		self.assertEquals(response.context["lastname"], "lastname")
		self.assertTemplateUsed(response, "mainapp/signup.html")

	def test_signup_user_create_object(self):
		context = {
			"SIGNUP": "",
			"first_name": "firstname",
			"last_name": "lastname",
			"email": "newemail@email.com",
			"password": "RandomPassword123"
		}
		response = self.client.post(self.url, context)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.context["message"], "Account created successfully.")
		self.assertTrue(User.objects.filter(username="newemail@email.com").exists());
		self.assertTemplateUsed(response, "mainapp/signup.html")