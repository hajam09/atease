from django.contrib.auth.models import User
from django.db import connection
from faker import Faker
from mainapp.models import Countries
from mainapp.models import GeneralPractice
from mainapp.models import Patient
from random import randint
import random
import string

def install_patients():
	all_tables = connection.introspection.table_names()
	if 'mainapp_patient' not in all_tables:
		return

	if Patient.objects.all().count() >= 100:
		return

	list_of_patients = []
	all_gps = GeneralPractice.objects.all()

	for i in range(10):
		fake = Faker()
		firstname = fake.unique.first_name()
		lastname = fake.unique.last_name()
		email = firstname+'.'+lastname+'@yahoo.com'
		email = email.lower()
		password = "A1b2C3d4E5f6G7h"

		if User.objects.filter(username=email).exists():
			continue

		user = User.objects.create_user(username=email, email=email, password=password, first_name=firstname, last_name=lastname)
		user.save()

		address_1 = str(randint(1, 100)) + " " + fake.unique.first_name() + " " + "Road"
		alphabet = list(string.ascii_uppercase)
		postalZip = random.choice(alphabet) + random.choice(alphabet) + str(randint(1, 100)) + " " + str(randint(1, 10)) + random.choice(alphabet) + random.choice(alphabet)

		year = str(randint(1930, 2021))
		month = str(randint(1, 12))

		if len(month) == 1:
			month = "0" + month

		day = str(randint(1, 28))
		if len(day) == 1:
			day = "0" + day

		date_of_birth = year + "-" + month + "-" + day

		location = {
			"address_1": address_1,
			"address_2": fake.unique.last_name(),
			"city": "London",
			"stateProvince": "Essex",
			"postalZip": postalZip,
			"country": {
				"alpha": "GB",
				"name": "United Kingdom"
			}
		}

		Patient.objects.create(
			user = user,
			date_of_birth = date_of_birth,
			address = location,
			mobile = "+44"+str(randint(7000000000, 7999999999)),
			nhs_number = str(randint(70000000, 79999999)),
			blood_group = random.choice(['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']),
			patient_at = random.choice(all_gps)
		)

	if len(list_of_patients) == 0:
		return

	Patient.objects.bulk_create(list_of_patients)
	return

def install_gp():
	all_tables = connection.introspection.table_names()
	if 'mainapp_generalpractice' not in all_tables:
		return
	if GeneralPractice.objects.all().count() > 20:
		return

	list_of_gps = []

	for i in range(2):
		fake = Faker()
		name = fake.name() + " Surgery"
		letters = string.ascii_lowercase
		registration_number = ''.join(random.choice(letters) for i in range(10))
		contact_number = "+44"+str(randint(7000000000, 7999999999))

		address_1 = str(randint(1, 100)) + " " + name
		alphabet = list(string.ascii_uppercase)
		postalZip = random.choice(alphabet) + random.choice(alphabet) + str(randint(1, 100)) + " " + str(randint(1, 10)) + random.choice(alphabet) + random.choice(alphabet)

		location = {
			"address_1": address_1,
			"address_2": fake.unique.last_name(),
			"city": "London",
			"stateProvince": "Essex",
			"postalZip": postalZip,
			"country": {
				"alpha": "GB",
				"name": "United Kingdom"
			}
		}

		open_times = {
			"monday": {
				"from": "09:30",
				"to": "05:30"
			},
			"tuesday": {
				"from": "09:30",
				"to": "05:30"
			},
			"wednesday": {
				"from": "09:30",
				"to": "05:30"
			},
			"monday": {
				"from": "09:30",
				"to": "05:30"
			},
			"thursday": {
				"from": "09:30",
				"to": "05:30"
			},
			"friday": {
				"from": "09:30",
				"to": "05:30"
			}
		}

		list_of_gps.append(
			GeneralPractice(
				name = name,
				registration_number = registration_number,
				contact_number = contact_number,
				address = location,
				open_times = open_times,
			)
		)

	if len(list_of_gps) == 0:
		return

	GeneralPractice.objects.bulk_create(list_of_gps)
	return

def install_countries():
	all_tables = connection.introspection.table_names()

	if 'mainapp_countries' not in all_tables:
		return

	list_of_countries = []

	for i in open("seed-data/countries.txt", "r").readlines():
		i = i.replace("\n", "").split("|")
		if not Countries.objects.filter(alpha=i[0]).exists():
			list_of_countries.append(
				Countries(
					alpha=i[0],
					name=i[1]
				)
			)

	if len(list_of_countries) == 0:
		return
	
	Countries.objects.bulk_create(list_of_countries)
	return