from django.urls import path
from django.urls import include
from mainapp import views
app_name = "mainapp"

urlpatterns = [
	path('', views.mainpage, name='mainpage'),
	path('account/login/', views.login, name='login'),
	path('account/logout/', views.logout, name='logout'),
	path('account/forgetpassword/', views.forgetpassword, name='forgetpassword'),
	path('account/signup/', views.signup, name='signup'),
	path('profile/patient/', views.patient_profile, name='patient_profile'),
	path('profile/doctor/', views.doctor_profile, name='doctor_profile'),
	path('profile/nurse/', views.nurse_profile, name='nurse_profile'),
	path('profile/receptionist/', views.receptionist_profile, name='receptionist_profile'),
	path('profile/', views.create_profile, name='create_profile'),
	path('gp_view/', views.gp_view, name='gp_view'),
	path('staff_only/<slug:patient_id>/', views.patient_view, name='patient_view'),
	path('verify/<slug:code>/', views.verify_view, name='verify_view'),
]