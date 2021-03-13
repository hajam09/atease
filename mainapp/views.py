from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from http import HTTPStatus
from mainapp.forms import GPMedicalRecordsForm
from mainapp.forms import MyMedicalRecordsForm
from mainapp.models import Appointments
from mainapp.models import Countries
from mainapp.models import Doctor
from mainapp.models import GPCurrentMedication
from mainapp.models import GPMedicalRecords
from mainapp.models import GeneralPractice
from mainapp.models import HealthAdvice
from mainapp.models import MyCurrentMedication
from mainapp.models import MyMedicalRecords
from mainapp.models import Notes
from mainapp.models import Nurse
from mainapp.models import Patient
from mainapp.models import Receptionist
from mainapp.utils import install_countries
from mainapp.utils import install_gp
from mainapp.utils import install_patients
import datetime
import json
import pandas as pd
import uuid

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

	if request.is_ajax():
		TASK = request.GET.get('TASK', None)

		if TASK == "search_for_gp":
			gp_code = request.GET.get('gp_code', None)
			get_gps = GeneralPractice.objects.filter(registration_number=gp_code)
			if get_gps.exists():
				gp_object = get_gps[0]
				the_data = {
					"gp_name": gp_object.name,
					"address_1": gp_object.address["address_1"],
					"address_2": gp_object.address["address_2"],
					"city": gp_object.address["city"],
					"postal_zip": gp_object.address["postalZip"],
					"contact_number": gp_object.contact_number,
				}
				return HttpResponse(json.dumps({"found": True, "data": the_data}), content_type="application/json")
			return HttpResponse(json.dumps({"found": False}), content_type="application/json")

	if request.method == "POST" and "patient_profile" in request.POST:
		date_of_birth = request.POST['date_of_birth']
		mobile_number = request.POST['mobile_number']
		nhs_number = request.POST['nhs_number']
		blood_group = request.POST['blood_group']
		gp_code = request.POST['gp_code']

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

		the_gp = GeneralPractice.objects.filter(registration_number=gp_code)
		if not the_gp.exists():
			messages.add_message(request,messages.SUCCESS, "No GP found.")
			return redirect('mainapp:create_profile')


		Patient.objects.create(
			user = request.user,
			date_of_birth = date_of_birth,
			address = location,
			mobile = mobile_number,
			nhs_number = nhs_number,
			blood_group = blood_group,
			patient_at = the_gp[0]
		)
		return redirect('mainapp:patient_profile')

	if request.method == "POST" and "staff_profile" in request.POST:
		role = request.POST['role']
		gp_code = request.POST['gp_code_for_staff']
		weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
		schedule = ['from', 'to']
		workingHours = {}

		the_gp = GeneralPractice.objects.filter(registration_number=gp_code)
		if not the_gp.exists():
			messages.add_message(request,messages.SUCCESS, "No GP found.")
			return redirect('mainapp:create_profile')

		for i in weekdays:
			workingHours[i] = {
				'from': request.POST[i+'_from'],
				'to': request.POST[i+'_to']
			}

		if role == 'doctor':
			print("creating doctor role")
			Doctor.objects.create(
				user = request.user,
				works_at = the_gp[0],
				working_hours = workingHours
			)
			return redirect('mainapp:doctor_profile')
			
		elif role == 'nurse':
			print("creating nurse role")
			Nurse.objects.create(
				user = request.user,
				works_at = the_gp[0],
				working_hours = workingHours
			)

			return redirect('mainapp:nurse_profile')
		elif role == 'receptionist':
			print("creating receptionist role")
			Receptionist.objects.create(
				user = request.user,
				works_at = the_gp[0],
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

		if patient.user.email != email:
			patient.email_verified = False

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

	if request.method == 'POST' and "CreateAppointment" in request.POST:
		# make below fields be mandatory in post on the template.
		appointmentDate = request.POST['appointmentDate']
		appointmentTime = request.POST['appointmentTime']
		availableDoctor = request.POST['availableDoctor']
		appointmentTimeSet = appointmentDate+"T"+appointmentTime

		requestedDoctor = Doctor.objects.get(id=availableDoctor)

		if not Appointments.objects.filter(
			doctor=requestedDoctor,
			time__year=appointmentDate.split("-")[0],
			time__month=appointmentDate.split("-")[1],
			time__day=appointmentDate.split("-")[2],
			time__hour=appointmentTime.split(":")[0],
			time__minute=appointmentTime.split(":")[1]).exists():
			Appointments.objects.create(
				doctor=requestedDoctor,
				user=request.user,
				time=appointmentTimeSet
			)
			msg = "An appointment has been created for you at {} {} with {}".format(appointmentDate, appointmentTime, requestedDoctor.user.get_full_name())
			messages.add_message(request,messages.SUCCESS, msg)
			return redirect('mainapp:patient_profile')

		msg = "Error creating an appointment. Please try again later."
		messages.add_message(request,messages.SUCCESS, msg)
		return redirect('mainapp:patient_profile')

	if request.is_ajax():
		TASK = request.GET.get('TASK', None)

		if TASK == 'verify_email':
			new_verification_code = str(uuid.uuid4())
			patient.verification_data["verification_code"] = new_verification_code
			patient.save()

			link = "http://localhost:8000/verify/{}/".format(new_verification_code)

			email_subject = "Activate your AtEase email."
			message = """
			Hi {},
				Please click the link below to activate your email.
				Link: {}

			Thanks,
			Management
			""".format(patient.user.get_full_name(), link)
			email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [patient.user.email])
			email_message.send()
			return HttpResponse(json.dumps({"message": "Verification link has been sent to your email."}), content_type="application/json")

		if TASK == 'deleteMyMedicalRecords':
			document_id = request.GET.get('document_id', None)
			instance = MyMedicalRecords.objects.get(id=document_id)
			instance.delete()
			return HttpResponse(json.dumps({}), content_type="application/json")

		if TASK == 'fetch_available_dates':
			chosenDate = request.GET.get('chosenDate', None)
			weekday = request.GET.get('weekday', None)

			gp_open_from = patient.patient_at.open_times[weekday]["from"]
			gp_open_to = patient.patient_at.open_times[weekday]["to"]
			gp_open_to_split = gp_open_to.split(":")
			new_48_time_end_time = str(int(gp_open_to_split[0])+12) + ":" + gp_open_to_split[1]

			# list of appointment times for the gp through out the specified date.
			available_times = list(pd.date_range(gp_open_from, new_48_time_end_time, freq="10min").time)
			time_slot = {str(i)[0:5]: 0 for i in available_times}
			_all_doc = Doctor.objects.filter(works_at=patient.patient_at)

			# in the time slot for each day, check number of doctors filled.
			for doc in _all_doc:
				doc_appointments = Appointments.objects.filter(doctor=doc, time__year=chosenDate.split("-")[0],
					time__month=chosenDate.split("-")[1], time__day=chosenDate.split("-")[2])
				
				for i in doc_appointments:
					time_slot[str(i.time.time())[0:5]] += 1

			free_slot = [k for k, v in time_slot.items() if v!=_all_doc.count()]
			return HttpResponse(json.dumps({"free_slot": free_slot}), content_type="application/json")

		if TASK == 'fetch_available_doctors':
			chosenDate = request.GET.get('chosenDate', None)
			chosenTime = request.GET.get('chosenTime', None)

			_all_doc = Doctor.objects.filter(works_at=patient.patient_at)
			free_doctor = []

			for doc in _all_doc:
				if not Appointments.objects.filter(
					doctor=doc,
					time__year=chosenDate.split("-")[0],
					time__month=chosenDate.split("-")[1],
					time__day=chosenDate.split("-")[2],
					time__hour=chosenTime.split(":")[0],
					time__minute=chosenTime.split(":")[1]).exists():
					free_doctor.append({"doctor_name": doc.user.get_full_name(), "doctor_object_id": doc.id})
			return HttpResponse(json.dumps({"free_doctors": free_doctor }), content_type="application/json")

		if TASK == 'delete_this_appointment':
			appointmentId = request.GET.get('appointmentId', None)
			Appointments.objects.filter(id=int(appointmentId)).delete()
			return HttpResponse(json.dumps({"status_code": 200}), content_type="application/json")

	# this user's appointment
	appointments = Appointments.objects.filter(user=request.user)
	appointments_data = []
	for a in appointments:
		startTime = a.time
		endTime = startTime + datetime.timedelta(minutes = 10)
		appointments_data.append({
			"pk": a.pk,
			"title": a.doctor.user.get_full_name(),
			"start": startTime.strftime("%Y-%m-%dT%H:%M:00"),
			"end": endTime.strftime("%Y-%m-%dT%H:%M:00"),
		})

	context = {
		"documents": MyMedicalRecords.objects.filter(user=request.user),
		'form': form,
		"patient": patient,
		"countries": Countries.objects.all(),
		"notes": Notes.objects.filter(user=request.user),
		"gp_medication": GPCurrentMedication.objects.filter(prescribed_to=patient),
		"my_medication": MyCurrentMedication.objects.filter(user=request.user),
		"gp_medical_record_documents": GPMedicalRecords.objects.filter(prescribed_to=patient, access_to_patient=True),
		"appointments": appointments_data,
	}
	return render(request,"mainapp/patient_profile.html", context)

@login_required
def doctor_profile(request):
	try:
		doctor = Doctor.objects.get(user=request.user)
	except Doctor.DoesNotExist:
		raise e

	if request.method == "POST" and "UpdateDoctorProfile" in request.POST:
		first_name = request.POST["first_name"]
		last_name = request.POST["last_name"]
		email = request.POST["email"]

		if doctor.user.email != email:
			doctor.email_verified = False

		doctor.user.first_name = first_name
		doctor.user.last_name = last_name
		doctor.user.email = email
		doctor.save()
		doctor.user.save()
		return redirect('mainapp:doctor_profile')

	if request.is_ajax():
		TASK = request.GET.get('TASK', None)

		if TASK == 'verify_email':
			new_verification_code = str(uuid.uuid4())
			doctor.verification_data["verification_code"] = new_verification_code
			doctor.save()

			link = "http://localhost:8000/verify/{}/".format(new_verification_code)

			email_subject = "Activate your AtEase email."
			message = """
			Hi {},
				Please click the link below to activate your email.
				Link: {}

			Thanks,
			Management
			""".format(doctor.user.get_full_name(), link)
			email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [doctor.user.email])
			email_message.send()
			return HttpResponse(json.dumps({"message": "Verification link has been sent to your email."}), content_type="application/json")

		if TASK == 'delete_this_appointment':
			appointmentId = request.GET.get('appointmentId', None)
			Appointments.objects.filter(id=int(appointmentId)).delete()
			return HttpResponse(json.dumps({"status_code": 200}), content_type="application/json")

	appointments = Appointments.objects.filter(doctor=doctor)
	data = []
	for a in appointments:
		startTime = a.time
		endTime = startTime + datetime.timedelta(minutes = 10)
		data.append({
			"pk": a.pk,
			"title": a.user.get_full_name(),
			"start": startTime.strftime("%Y-%m-%dT%H:%M:00"),
			"end": endTime.strftime("%Y-%m-%dT%H:%M:00"),
		})
	context = {
		"doctor": doctor,
		"appointments": data
	}
	return render(request,"mainapp/doctor_profile.html", context)

@login_required
def nurse_profile(request):
	try:
		nurse = Nurse.objects.get(user=request.user)
	except Nurse.DoesNotExist:
		raise e

	if request.is_ajax():
		TASK = request.GET.get('TASK', None)

		if TASK == 'verify_email':
			new_verification_code = str(uuid.uuid4())
			nurse.verification_data["verification_code"] = new_verification_code
			nurse.save()

			link = "http://localhost:8000/verify/{}/".format(new_verification_code)

			email_subject = "Activate your AtEase email."
			message = """
			Hi {},
				Please click the link below to activate your email.
				Link: {}

			Thanks,
			Management
			""".format(nurse.user.get_full_name(), link)
			email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [nurse.user.email])
			email_message.send()
			return HttpResponse(json.dumps({"message": "Verification link has been sent to your email."}), content_type="application/json")
	return render(request,"mainapp/nurse_profile.html", {})

@login_required
def receptionist_profile(request):

	try:
		receptionist = Receptionist.objects.get(user=request.user)
	except Receptionist.DoesNotExist:
		raise e

	if request.method == "POST" and "UpdateReceptionistProfile" in request.POST:
		first_name = request.POST["first_name"]
		last_name = request.POST["last_name"]
		email = request.POST["email"]

		if receptionist.user.email != email:
			receptionist.email_verified = False

		receptionist.user.first_name = first_name
		receptionist.user.last_name = last_name
		receptionist.user.email = email
		receptionist.save()
		receptionist.user.save()
		return redirect('mainapp:doctor_profile')

	if request.is_ajax():
		TASK = request.GET.get('TASK', None)

		if TASK == 'verify_email':
			new_verification_code = str(uuid.uuid4())
			receptionist.verification_data["verification_code"] = new_verification_code
			receptionist.save()

			link = "http://localhost:8000/verify/{}/".format(new_verification_code)

			email_subject = "Activate your AtEase email."
			message = """
			Hi {},
				Please click the link below to activate your email.
				Link: {}

			Thanks,
			Management
			""".format(receptionist.user.get_full_name(), link)
			email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [receptionist.user.email])
			email_message.send()
			return HttpResponse(json.dumps({"message": "Verification link has been sent to your email."}), content_type="application/json")

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

		the_gp = account_object.works_at
		the_gp.open_times = workingHours
		the_gp.save()
		return redirect('mainapp:gp_view')

	if request.method == 'POST' and "search_for_patients" in request.POST:
		patient_name = request.POST['patient_name'].title().split(" ")

		# Get all the patients within the gp of the authenticated user.
		if account_object:
			the_gp = account_object.works_at
			if patient_name[0] != '':
				patients_of_this_gp = Patient.objects.filter(patient_at=the_gp, user__first_name__in=patient_name) | Patient.objects.filter(patient_at=the_gp, user__last_name__in=patient_name)
				context["patients"] = patients_of_this_gp
			else:
				context["patients"] = Patient.objects.filter(patient_at=the_gp)
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

		if TASK == 'allowGPMedicalRecordsAccessToPatient':
			document_id = request.GET.get('document_id', None)
			instance = GPMedicalRecords.objects.get(id=document_id)
			instance.access_to_patient = True
			instance.save()
			return HttpResponse(json.dumps({}), content_type="application/json")

		if TASK == 'denyGPMedicalRecordsAccessToPatient':
			document_id = request.GET.get('document_id', None)
			instance = GPMedicalRecords.objects.get(id=document_id)
			instance.access_to_patient = False
			instance.save()
			return HttpResponse(json.dumps({}), content_type="application/json")

	context = {
		"patient": patient,
		"countries": Countries.objects.all(),
		"form": form,
		"documents": GPMedicalRecords.objects.filter(prescribed_to=patient),
		"gp_medication": GPCurrentMedication.objects.filter(prescribed_to=patient),
	}
	return render(request,"mainapp/patient_view.html", context)

def verify_view(request, code):
	patient = Patient.objects.filter(verification_data__contains={"verification_code": code})
	doctor = Doctor.objects.filter(verification_data__contains={"verification_code": code})
	nurse = Nurse.objects.filter(verification_data__contains={"verification_code": code})
	receptionist = Receptionist.objects.filter(verification_data__contains={"verification_code": code})

	if patient.exists():
		this_patient_object = patient[0]
		this_patient_object.email_verified = True
		this_patient_object.save()

	elif doctor.exists():
		this_doctor_object = doctor[0]
		this_doctor_object.email_verified = True
		this_doctor_object.save()

	elif nurse.exists():
		this_nurse_object = nurse[0]
		this_nurse_object.email_verified = True
		this_nurse_object.save()

	elif receptionist.exists():
		this_receptionist_object = receptionist[0]
		this_receptionist_object.email_verified = True
		this_receptionist_object.save()

	return redirect('mainapp:mainpage')