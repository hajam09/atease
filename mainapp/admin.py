from django.contrib import admin
from .models import *

admin.site.register(GeneralPractice)
admin.site.register(Profile)
admin.site.register(Doctor)
admin.site.register(Appointments)
admin.site.register(MyMedicalRecords)
admin.site.register(GPMedicalRecords)
admin.site.register(GPCurrentMedication)
admin.site.register(Notes)
admin.site.register(MyCurrentMedication)
admin.site.register(HospitalAccount)