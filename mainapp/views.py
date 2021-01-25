from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout as auth_logout, login as auth_login
from django.http import HttpResponse
from http import HTTPStatus
from .models import *

def login(request):

	"""
	TODO: return to main page after login.
	Redirect to forgetpassword page on the tempalte.
	redirect to signup page on the template.
	"""

	if request.method == 'POST' and 'LOGIN' in request.POST:
		username = request.POST['email']
		password = request.POST['password']

		if not request.POST.get('user_remember', None):
			request.session.set_expiry(0)

		user = authenticate(username=username, password=password)
		if user:
			auth_login(request, user)
			# return redirect('tutoring:mainpage')
		else:
			context = {
				"message": "Username or Password did not match!",
			}
			return render(request,"mainapp/login.html", context)

	return render(request,"mainapp/login.html", {})

def logout(request):
	auth_logout(request)
	return redirect('mainapp:login')