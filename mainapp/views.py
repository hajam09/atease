from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout as auth_logout, login as auth_login
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from http import HTTPStatus
from .models import *
from .utils import *
from .forms import MyMedicalRecordsForm

def login(request):

	if request.method == 'POST' and 'LOGIN' in request.POST:
		username = request.POST['email']
		password = request.POST['password']

		if not request.POST.get('user_remember', None):
			request.session.set_expiry(0)

		user = authenticate(username=username, password=password)
		if user:
			auth_login(request, user)
			return redirect('mainapp:mainpage')
		else:
			context = {
				"message": "Username or Password did not match!",
			}
			return render(request,"mainapp/login.html", context)

	return render(request,"mainapp/login.html", {})

def logout(request):
	auth_logout(request)
	return redirect('mainapp:login')

def forgetpassword(request):
	return render(request,"mainapp/forgetpassword.html", {})

def signup(request):

	if request.method == 'POST' and 'SIGNUP' in request.POST:
		firstname = request.POST['first_name']
		lastname = request.POST['last_name']
		email = request.POST['email']
		password = request.POST['password']

		if User.objects.filter(username=email).exists():
			context = {
				"message": "An account already exists for this email address!",
				"email": email,
				"firstname": firstname,
				"lastname": lastname
			}
			return render(request,"mainapp/signup.html", context)
		else:
			if(len(password)<8 or any(letter.isalpha() for letter in password)==False or any(capital.isupper() for capital in password)==False or any(number.isdigit() for number in password)==False):
				context = {
					"message": "Your password is not strong enough.",
					"email": email,
					"firstname": firstname,
					"lastname": lastname
				}
				return render(request,"mainapp/signup.html", context)

			user = User.objects.create_user(username=email, email=email, password=password, first_name=firstname, last_name=lastname)
			user.save()

			context = {
				"message": "Account created successfully.",
			}

			return render(request,"mainapp/signup.html", context)


	return render(request,"mainapp/signup.html", {})

def mainpage(request):
	return render(request,"mainapp/mainpage.html", {})

@login_required
def create_profile(request):
	if Patient.objects.filter(user=request.user).exists():
		return redirect('mainapp:patient_profile')

	if Doctor.objects.filter(user=request.user).exists():
		return redirect('mainapp:doctor_profile')

	if request.method == "POST" and "patient_profile" in request.POST:
		# Patient cretates an account
		date_of_birth = request.POST['date_of_birth']
		mobile_number = request.POST['mobile_number']
		nhs_number = request.POST['nhs_number']
		blood_group = request.POST['blood_group']
		list_of_gps = request.POST['list_of_gps']

		country = Countries.objects.get(alpha=request.POST["country"])
		location = {
			"address_1": request.POST["address_1"].strip().title(),
			"address_2": request.POST["address_2"].strip().title(),
			"city": request.POST["city"].strip().title(),
			"stateProvice": request.POST["stateProvice"].strip().title(),
			"postalZip": request.POST["postalZip"].strip().upper(),
			"country": {
				"alpha": country.alpha,
				"name": country.name
			}
		}

		Patient.objects.create(
			user = request.user,
			dateOfBirth = date_of_birth,
			address = location,
			mobile = mobile_number,
			nhsNumber = nhs_number,
			bloodGroup = blood_group,
			generalPractice = GeneralPractice.objects.get(id=list_of_gps)
		)
		# Patient object created
		return redirect('mainapp:patient_profile')

	if request.method == "POST" and "doctor_profile" in request.POST:
		doctor_name = request.POST['doctor_name']
		list_of_gps = request.POST['list_of_gps']
		weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
		schedule = ['from', 'to']
		workingHours = {}

		for i in weekdays:
			workingHours[i] = {
				'from': request.POST[i+'_from'],
				'to': request.POST[i+'_to']
			}

		Doctor.objects.create(
			user = request.user,
			name = doctor_name,
			generalPractice = GeneralPractice.objects.get(id=list_of_gps),
			workingHours = workingHours
		)
		# Doctor object created
		return redirect('mainapp:doctor_profile')

	context = {
		"countries": Countries.objects.all(),
		"gps": GeneralPractice.objects.all(),
	}

	return render(request,"mainapp/create_profile.html", context)

@login_required
def patient_profile(request):
	try:
		patient = Patient.objects.get(user=request.user)
	except Patient.DoesNotExist:
		raise e

	if request.method == "POST" and "UPDATEPATIENTPROFILE" in request.POST:
		first_name = request.POST['first_name']
		last_name = request.POST['last_name']
		email = request.POST['email']
		mobile = request.POST['mobile']

		patient.mobile = mobile
		patient.user.first_name = first_name
		patient.user.last_name = last_name
		patient.user.email = email
		patient.save()
		patient.user.save()
		return redirect('mainapp:patient_profile')

	if request.method == "POST" and "UPDATEPATIENTADDRESS" in request.POST:
		country = Countries.objects.get(alpha=request.POST["country"])
		location = {
			"address_1": request.POST["address_1"].strip().title(),
			"address_2": request.POST["address_2"].strip().title(),
			"city": request.POST["city"].strip().title(),
			"stateProvice": request.POST["stateProvice"].strip().title(),
			"postalZip": request.POST["postalZip"].strip().upper(),
			"country": {
				"alpha": country.alpha,
				"name": country.name
			}
		}
		patient.address = location
		patient.save()
		return redirect('mainapp:patient_profile')

	# Handle file upload
	if request.method == 'POST' and "UPLOADMYMEDICALRECORDDOCUMENTS" in request.POST:
		form = MyMedicalRecordsForm(request.POST, request.FILES)
		if form.is_valid():
			newdoc = MyMedicalRecords(user=request.user,document = request.FILES['docfile'])
			newdoc.save()

			# Redirect to the document list after POST
			return redirect('mainapp:patient_profile')
	else:
		form = MyMedicalRecordsForm() # A empty, unbound form

	context = {
		"documents": MyMedicalRecords.objects.all(),
		'form': form,
		"patient": patient,
		"countries": Countries.objects.all(),
	}
	return render(request,"mainapp/patient_profile.html", context)

@login_required
def doctor_profile(request):
	return render(request,"mainapp/doctor_profile.html", {})