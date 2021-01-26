from .models import Countries
from django.db import connection

def install_countries():
	all_tables = connection.introspection.table_names()

	if 'mainapp_countries' not in all_tables:
		return

	for i in open("seed-data/countries.txt", "r").readlines():
		i = i.replace("\n", "").split("|")
		if not Countries.objects.filter(alpha=i[0]).exists():
			Countries.objects.create(alpha=i[0], name=i[1])

	print("Countries table created and populated")
	return

install_countries()