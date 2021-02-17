from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout as auth_logout, login as auth_login
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from http import HTTPStatus
from .models import *
from .utils import *
from .forms import MyMedicalRecordsForm, GPMedicalRecordsForm
import json

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
	context = {
		"health_advice": HealthAdvice.objects.all()
	}
	return render(request,"mainapp/mainpage.html", context)

@login_required
def create_profile(request):
	if Patient.objects.filter(user=request.user).exists():
		return redirect('mainapp:patient_profile')

	if Doctor.objects.filter(user=request.user).exists():
		return redirect('mainapp:doctor_profile')

	if Nurse.objects.filter(user=request.user).exists():
		return redirect('mainapp:nurse_profile')

	if Receptionist.objects.filter(user=request.user).exists():
		return redirect('mainapp:receptionist_profile')

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
			"stateProvince": request.POST["stateProvince"].strip().title(),
			"postalZip": request.POST["postalZip"].strip().upper(),
			"country": {
				"alpha": country.alpha,
				"name": country.name
			}
		}

		Patient.objects.create(
			user = request.user,
			date_of_birth = date_of_birth,
			address = location,
			mobile = mobile_number,
			nhs_number = nhs_number,
			blood_group = blood_group,
			patient_at = GeneralPractice.objects.get(id=list_of_gps)
		)
		# Patient object created
		return redirect('mainapp:patient_profile')

	if request.method == "POST" and "staff_profile" in request.POST:
		role = request.POST['role']
		list_of_gps = request.POST['list_of_gps']
		weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
		schedule = ['from', 'to']
		workingHours = {}
		print("rolerolerolerole", role)

		for i in weekdays:
			workingHours[i] = {
				'from': request.POST[i+'_from'],
				'to': request.POST[i+'_to']
			}

		if role == 'doctor':
			print("creating doctor role")
			Doctor.objects.create(
				user = request.user,
				works_at = GeneralPractice.objects.get(id=list_of_gps),
				working_hours = workingHours
			)
			return redirect('mainapp:doctor_profile')
			
		elif role == 'nurse':
			print("creating nurse role")
			Nurse.objects.create(
				user = request.user,
				works_at = GeneralPractice.objects.get(id=list_of_gps),
				working_hours = workingHours
			)

			return redirect('mainapp:nurse_profile')
		elif role == 'receptionist':
			print("creating receptionist role")
			Receptionist.objects.create(
				user = request.user,
				works_at = GeneralPractice.objects.get(id=list_of_gps),
				working_hours = workingHours
			)
			return redirect('mainapp:receptionist_profile')

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
			"stateProvince": request.POST["stateProvince"].strip().title(),
			"postalZip": request.POST["postalZip"].strip().upper(),
			"country": {
				"alpha": country.alpha,
				"name": country.name
			}
		}
		patient.address = location
		patient.save()
		return redirect('mainapp:patient_profile')

	if request.method == 'POST' and "CREATENOTES" in request.POST:
		title = request.POST["title"]
		description = request.POST["description"]

		Notes.objects.create(
			user = request.user,
			title = title,
			description = description,
		)

		return redirect('mainapp:patient_profile')

	if request.method == 'POST' and "Create_My_Current_Medication" in request.POST:
		name = request.POST['name']
		description = request.POST['description']
		start_date = request.POST['start_date']

		MyCurrentMedication.objects.create(
			user = request.user,
			name = name,
			description = description,
			start_date = start_date,
		)
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

	if request.method == 'POST' and "DELETENOTES" in request.POST:
		notes_id = request.POST['notes_id']
		Notes.objects.get(id=notes_id).delete()
		return redirect('mainapp:patient_profile')

	if request.method == 'POST' and "DELETE_my_medication" in request.POST:
		my_medication_id = request.POST['my_medication_id']
		MyCurrentMedication.objects.get(id=my_medication_id).delete()
		return redirect('mainapp:patient_profile')

	if request.is_ajax():
		TASK = request.GET.get('TASK', None)

		if TASK == 'deleteMyMedicalRecords':
			document_id = request.GET.get('document_id', None)
			instance = MyMedicalRecords.objects.get(id=document_id)
			instance.delete()
			return HttpResponse(json.dumps({}), content_type="application/json")

	context = {
		"documents": MyMedicalRecords.objects.filter(user=request.user),
		'form': form,
		"patient": patient,
		"countries": Countries.objects.all(),
		"notes": Notes.objects.filter(user=request.user),
		"gp_medication": GPCurrentMedication.objects.filter(prescribed_to=patient),
		"my_medication": MyCurrentMedication.objects.filter(user=request.user),
	}
	return render(request,"mainapp/patient_profile.html", context)

@login_required
def doctor_profile(request):
	try:
		doctor = Doctor.objects.get(user=request.user)
	except Doctor.DoesNotExist:
		raise e
	context = {
		"doctor": doctor
	}
	return render(request,"mainapp/doctor_profile.html", context)

@login_required
def nurse_profile(request):
	return render(request,"mainapp/nurse_profile.html", {})

@login_required
def receptionist_profile(request):

	try:
		receptionist = Receptionist.objects.get(user=request.user)
	except Receptionist.DoesNotExist:
		raise e
	context = {
		"receptionist": receptionist
	}
	return render(request,"mainapp/receptionist_profile.html", context)

@login_required
def gp_view(request):

	context = {}

	try:
		account_object = Doctor.objects.get(user=request.user)
	except:

		try:
			account_object = Nurse.objects.get(user=request.user)
		except:
			account_object = Receptionist.objects.get(user=request.user)

	context["can_edit_opening_times"] = True if isinstance(account_object, Receptionist) else False
	context["profile"] = account_object


	
	if request.method == 'POST' and "Update_GP_Hours" in request.POST and isinstance(account_object, Receptionist):

		weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
		schedule = ['from', 'to']
		workingHours = {}

		for i in weekdays:
			workingHours[i] = {
				'from': request.POST[i+'_from'],
				'to': request.POST[i+'_to']
			}

		print(workingHours)

		the_gp = account_object.works_at
		the_gp.open_times = workingHours
		the_gp.save()
		return redirect('mainapp:gp_view')



	if request.method == 'POST' and "search_for_patients" in request.POST:
		patient_name = request.POST['patient_name']
		patient_name = patient_name.split(" ")
		first_name = ""
		last_name = ""
		
		if len(patient_name) == 1:
			first_name = patient_name[0]

		if len(patient_name) >= 2:
			first_name = patient_name[0]
			last_name = " ".join(patient_name[1:])

		# Get all the patients within the gp of the authenticated user.
		if account_object:
			the_gp = account_object.works_at

			patients_of_this_gp = Patient.objects.filter(patient_at=the_gp, user__first_name__icontains=first_name) | Patient.objects.filter(patient_at=the_gp, user__last_name__icontains=last_name)


		context["patients"] = patients_of_this_gp
	return render(request,"mainapp/gp_view.html", context)

def patient_view(request, patient_id):

	try:
		patient = Patient.objects.get(pk=patient_id)
	except Patient.DoesNotExist:
		raise e

	try:
		account_object = Doctor.objects.get(user=request.user)
	except:

		try:
			account_object = Nurse.objects.get(user=request.user)
		except:
			account_object = Receptionist.objects.get(user=request.user)

	if account_object:
		users_work_place = account_object.works_at

		if patient.patient_at != users_work_place:
			# Patient is not of the staff gp.
			return redirect('mainapp:gp_view')

	# Handle file upload
	if request.method == 'POST' and "UPLOADMYMEDICALRECORDDOCUMENTS" in request.POST:
		form = GPMedicalRecordsForm(request.POST, request.FILES)
		if form.is_valid():
			newdoc = GPMedicalRecords(prescribed_by=account_object,prescribed_to=patient,document = request.FILES['docfile'])
			newdoc.save()

			# Redirect to the document list after POST
			return redirect('mainapp:patient_view', patient_id=patient_id)
	else:
		form = GPMedicalRecordsForm() # A empty, unbound form


	if request.method == "POST" and "Create_GP_Current_Medication" in request.POST and isinstance(account_object, Doctor):
		name = request.POST['name']
		description = request.POST['description']
		start_date = request.POST['start_date']

		GPCurrentMedication.objects.create(
			prescribed_to = patient,
			prescribed_by = account_object,
			name = name,
			description = description,
			start_date = start_date,
		)
		return redirect('mainapp:patient_view', patient_id=patient_id)

	if request.method == "POST" and "DELETE_gp_medication" in request.POST and isinstance(account_object, Doctor):
		gp_medication_id = request.POST['gp_medication_id']
		GPCurrentMedication.objects.get(id=gp_medication_id).delete()
		return redirect('mainapp:patient_view', patient_id=patient_id)

	if request.is_ajax():
		TASK = request.GET.get('TASK', None)

		if TASK == 'deleteMyMedicalRecords':
			document_id = request.GET.get('document_id', None)
			instance = GPMedicalRecords.objects.get(id=document_id)
			instance.delete()
			return HttpResponse(json.dumps({}), content_type="application/json")

	context = {
		"patient": patient,
		"countries": Countries.objects.all(),
		"form": form,
		"documents": GPMedicalRecords.objects.filter(prescribed_to=patient),
		"gp_medication": GPCurrentMedication.objects.filter(prescribed_to=patient),
	}

	return render(request,"mainapp/patient_view.html", context)