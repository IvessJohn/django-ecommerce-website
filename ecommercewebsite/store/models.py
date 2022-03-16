from decimal import Decimal
import black
from django.db import models
from django.contrib.auth.models import User

from django_countries.fields import CountryField
from coupon_management.validations import validate_coupon
from coupon_management.models import Coupon, Discount

# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name: models.CharField = models.CharField(max_length=200, null=True, blank=False)
    email: models.CharField = models.CharField(max_length=200, blank=True)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name: models.CharField = models.CharField(max_length=200, blank=False)
    price: models.DecimalField = models.DecimalField(max_digits=11, decimal_places=2, blank=False, null=True)
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
    applied_coupon = models.OneToOneField(Coupon, on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self) -> str:
        return f"Order({self.id})-{self.customer.name}"

    @property
    def get_cart_price(self):
        orderitems = self.orderitem_set.all()
        return sum(item.get_total_price for item in orderitems)
    
    @property
    def get_final_price(self):
        return self.__calculate_final_price()

    @property
    def get_items_amount(self):
        orderitems = self.orderitem_set.all()
        return sum(item.quantity for item in orderitems)
    
    @property
    def requires_shipping(self):
        if len(self.orderitem_set.all()) == 0:
            return False
        return any(orderitem.product.digital == False for orderitem in self.orderitem_set.all())

    def apply_coupon(self, coupon_code):
        user: User = self.customer__set.all()[0].user

        status = validate_coupon(coupon_code=coupon_code, user=user)
        if status["valid"]:
            coupon: Coupon = Coupon.objects.get(code=coupon_code)
            coupon.use_coupon(user=user)

    
    def __calculate_final_price(self):
        full_price: Decimal = self.get_cart_price

        if self.applied_coupon:
            discount: Discount = self.applied_coupon.discount
            
            if discount.is_percentage:
                discount_percentage: int = min(discount.value, 100)
                discount_amount: Decimal = full_price * discount_percentage * 0.01
            else:
                discount_amount: Decimal = Decimal(discount.value)
            return max(full_price - discount_amount, 0)
        
        return full_price

        

class OrderItem(models.Model):
    product: models.ForeignKey = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, unique=False)
    order: models.ForeignKey = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, unique=False)
    quantity: models.IntegerField = models.IntegerField(default=0, null=True, blank=True)
    date_added: models.DateTimeField = models.DateTimeField(auto_now_add=True, null=True)

    @property
    def get_total_price(self):
        if self.product:
            return self.product.price * self.quantity
        return Decimal(0.0)


class ShippingInformation(models.Model):
    customer: models.ForeignKey = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, unique=False)
    order: models.ForeignKey = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, unique=False)
    address: models.CharField = models.CharField(max_length=200, null=False, blank=False)
    city: models.CharField = models.CharField(max_length=200, null=False, blank=False)
    state: models.CharField = models.CharField(max_length=200, null=False, blank=False)
    country: CountryField = CountryField(blank_label="Select country...", default="USA", blank=True)
    zipcode: models.CharField = models.CharField(max_length=200, null=False, blank=False)
    date_added: models.DateTimeField = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self) -> str:
        return self.address

    class Meta:
        verbose_name = "Shipping Information"
        verbose_name_plural = "Shipping Informations"

