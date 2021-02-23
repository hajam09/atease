from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from mainapp.utils import install_patients, install_gp
from unittest import skip

# coverage run --source=mainapp manage.py test mainapp
# coverage html

@skip("")
class TestViewLogin(TestCase):

	def setUp(self):
		self.client = Client()
		self.url = reverse('mainapp:login')
		install_gp()
		install_patients()
		self.user_1 = User.objects.order_by("?").first()

	def test_login_GET(self):
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "mainapp/login.html")

	def test_login_authenticate_valid_user(self):
		context = {
			"LOGIN": "",
			"email": self.user_1.email,
			"password": "A1b2C3d4E5f6G7h",
		}
		response = self.client.post(self.url, context)
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/')
		self.assertIn('_auth_user_id', self.client.session)
		self.assertEqual(int(self.client.session['_auth_user_id']), self.user_1.pk)

	def test_login_authenticate_invalid_user(self):
		context = {
			"email": "randomuser@gmail.com",
			"password": "qWeRtY1234",
			"LOGIN": ""
		}
		response = self.client.post(self.url, context)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.context["message"], "Username or Password did not match!")
		self.assertTemplateUsed(response, "mainapp/login.html")

	def test_logout(self):
		self.client.login(username=self.user_1.email, password='A1b2C3d4E5f6G7h')
		self.url = reverse('mainapp:logout')
		response = self.client.get(self.url)
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/account/login/')
		self.assertNotIn('_auth_user_id', self.client.session)