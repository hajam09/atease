from django.urls import path, include
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
	path('profile/', views.create_profile, name='create_profile'),
]