from django.urls import path, include
from mainapp import views
app_name = "mainapp"

urlpatterns = [
	# path('', views.mainpage, name='mainpage'),
	path('account/login', views.login, name='login'),
	path('account/logout', views.logout, name='logout'),
]