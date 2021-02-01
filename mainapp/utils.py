from .models import Countries, GeneralPractice, Patient
from django.db import connection
from faker import Faker
from django.contrib.auth.models import User
from random import randint
import random
import string

def install_patients():
	all_tables = connection.introspection.table_names()
	if 'mainapp_patient' not in all_tables:
		return

	if Patient.objects.all().count() >= 200:
		return

	for i in range(201):
		print(i)
		fake = Faker()
		firstname = fake.unique.first_name()
		lastname = fake.unique.last_name()
		email = firstname+'.'+lastname+'@yahoo.com'
		password = "A1b2c3d5e6"

		user = User.objects.create(
			username=email, email=email, password=password, first_name=firstname, last_name=lastname
		)

		location = {
			"address_1": "01 Edgware Road",
			"address_2": "Edgware",
			"city": "London",
			"stateProvice": "Essex",
			"postalZip": "HG77 6XE",
			"country": {
				"alpha": "GB",
				"name": "United Kingdom"
			}
		}

		Patient.objects.create(
			user = user,
			date_of_birth = '1998-07-04',
			address = location,
			mobile = "+44"+str(randint(7000000000, 7999999999)),
			nhs_number = str(randint(70000000, 79999999)),
			blood_group = "A+",
			patient_at = random.choice(GeneralPractice.objects.all())
		)
		
	return



def install_gp():
	all_tables = connection.introspection.table_names()
	if 'mainapp_generalpractice' not in all_tables:
		return
	if GeneralPractice.objects.all().count() > 15:
		return

	list_of_gps = []

	for i in range(16):
		fake = Faker()
		name = fake.name() + " Surgery"
		letters = string.ascii_lowercase
		registration_number = ''.join(random.choice(letters) for i in range(10))
		contact_number = "+44"+str(randint(7000000000, 7999999999))
		list_of_gps.append(
			GeneralPractice(
				name = name,
				registration_number = registration_number,
				contact_number = contact_number
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
	print("Countries table created and populated")
	return

install_countries()
install_gp()
install_patients()