from django.urls import path
from . import views

urlpatterns = [
   path('', views.index),
   path('login', views.login),
   path('logout', views.logout),
   path('sign', views.sign),
   path('listInvoice', views.listInvoices),
   path('listCustomer', views.listCustomer)

]