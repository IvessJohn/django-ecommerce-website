"""A script containing often-used methods, or the methods that should be moved to a
separate file due to their size.
"""
import json
from decimal import Decimal
from django.contrib.auth.models import User
from django.http import HttpRequest

from coupon_management.validations import validate_coupon
from coupon_management.models import Coupon, Discount

from .models import *


def get_device_id_from_request(request: HttpRequest) -> str:
    """Return the value of `deviceID` cookie."""
    device_id: str = "my_device"
    if "deviceID" in request.COOKIES:
        device_id = request.COOKIES.get("deviceID")

    return device_id


def get_customer(request: HttpRequest) -> Customer:
    """Get the current customer from the HTTP request (if authenticated) or
    using the value of `deviceID` cookie.
    Creates a new Customer if `deviceID` is new."""
    # If user is authenticated, get it straight from the request
    if request.user.is_authenticated:
        customer: Customer = request.user.customer
    else:
        # If not, get it using device_id
        device_id: str = get_device_id_from_request(request)

        customer, created = Customer.objects.get_or_create(device_id=device_id)
        # print(f"customer's device id: {device_id}")

    return customer


def get_order_data(request: HttpRequest) -> dict:
    """Get the current order data as a dictionary.
    Data is retrieved either from the database (if the user is authenticated),
    or from browser cookies (`cart` cookie created for unauthenticated users).
    """
    customer: Customer = get_customer(request)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    ordered_items = order.orderitem_set.all()
    items_amount = order.get_items_amount
    requires_shipping = order.requires_shipping

    return {
        "order": order,
        "ordered_items": ordered_items,
        "items_amount": items_amount,
        "requires_shipping": requires_shipping,
    }


def append_guest_customer_info(customer: Customer, data):
    """Save guest customer's name and email from `data`.
    
    :param customer: Customer - the customer object which info should be complemented
    :param data - the dictionary from which the data for `customer` is retrieved"""
    name = data["userFormData"]["name"]
    email = data["userFormData"]["email"]

    customer.email = email
    customer.name = name
    customer.save()
