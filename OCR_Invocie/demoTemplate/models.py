from django.db import models


# Create your models here.

class Invoice(models.Model):
    id_customer = models.CharField(max_length=50)
    id_invoice = models.CharField(max_length=50, unique=True)
    total_invocie = models.FloatField()
    date_invoice = models.DateTimeField()
    date = models.DateTimeField(auto_now_add=True)

class Customer(models.Model):
    id_customer = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=10)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    full_name = models.CharField(max_length=100)
    birthday = models.CharField(max_length=20)


class Admin(models.Model):
    id_customer = models.CharField(max_length=50, unique=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)


class Auth(models.Model):
    username = models.CharField(max_length=100)
    token = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
