from email.policy import default
import black
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name: models.CharField = models.CharField(max_length=200, null=True, blank=False)
    email: models.CharField = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name: models.CharField = models.CharField(max_length=200, blank=False)
    price: models.DecimalField = models.DecimalField(max_digits=9, decimal_places=2, blank=False, null=True)
    digital: models.BooleanField = models.BooleanField(default=False, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Order(models.Model):
    customer: models.ForeignKey = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered: models.DateTimeField = models.DateTimeField(auto_now_add=True, null=True)
    complete: models.BooleanField = models.BooleanField(default=False)
    transaction_id: models.CharField = models.CharField(max_length=100, null=True, unique=True)

    def __str__(self) -> str:
        return f"Order({self.id})-{self.customer.name}"


class OrderItem(models.Model):
    product: models.ForeignKey = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, unique=False)
    order: models.ForeignKey = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, unique=False)
    quantity: models.IntegerField = models.IntegerField(default=0, null=True, blank=True)
    date_added: models.DateTimeField = models.DateTimeField(auto_now_add=True, null=True)


class ShippingInformation(models.Model):
    customer: models.ForeignKey = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, unique=False)
    order: models.ForeignKey = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, unique=False)
    address: models.CharField = models.CharField(max_length=200, null=False, blank=False)
    city: models.CharField = models.CharField(max_length=200, null=False, blank=False)
    state: models.CharField = models.CharField(max_length=200, null=False, blank=False)
    zipcode: models.CharField = models.CharField(max_length=200, null=False, blank=False)
    date_added: models.DateTimeField = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self) -> str:
        return self.address