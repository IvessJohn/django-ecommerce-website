"""A script containing often-used methods, or the methods that should be moved to a
separate file due to their size.
"""
import json
from decimal import Decimal
from django.contrib.auth.models import User

from coupon_management.validations import validate_coupon
from coupon_management.models import Coupon, Discount

from .models import *


def get_device_id_from_request(request) -> str:
    """Return the value of `deviceID` cookie."""
    device_id: str = "my_device"
    if "deviceID" in request.COOKIES:
        device_id = request.COOKIES.get("deviceID")

    return device_id


def get_customer(request) -> Customer:
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


def get_order_data(request) -> dict:
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


def cookie_cart(request) -> dict:
    """Retrieve order information from the `cart` cookie."""
    ordered_items = []
    order = {"get_cart_price": 0, "get_items_amount": 0, "requires_shipping": False}
    items_amount = order["get_items_amount"]
    cart = {}

    if "cart" in request.COOKIES:
        cart = json.loads(request.COOKIES["cart"])

    for i in cart:
        if Product.objects.filter(id=i).exists():
            product_quantity: int = cart[i]["quantity"]
            if product_quantity > 0:
                product: Product = Product.objects.get(id=i)

                order["get_items_amount"] += product_quantity
                order["get_cart_price"] += product.price * product_quantity
                if product.digital == False:
                    order["requires_shipping"] = True

                ordered_item = {
                    "product": product,
                    "quantity": product_quantity,
                    "get_total_price": product.price * product_quantity,
                }

                ordered_items.append(ordered_item)

    items_amount = order["get_items_amount"]
    order["get_cart_price"] = str(order["get_cart_price"])

    return {
        "ordered_items": ordered_items,
        "order": order,
        "items_amount": items_amount,
        "requires_shipping": order["requires_shipping"],
    }


def append_guest_customer_info(customer: Customer, data):
    """Save guest customer's name and email from `data`."""
    name = data["userFormData"]["name"]
    email = data["userFormData"]["email"]

    customer.email = email
    customer.name = name
    customer.save()


def create_guest_order(request, data) -> tuple[Customer, Order]:
    """Create an order for a guest user.
    Creates a Customer objects that holds the entered email.
    """
    name = data["userFormData"]["name"]
    email = data["userFormData"]["email"]

    customer, created = Customer.objects.get_or_create(
        email=email,
    )
    customer.name = name
    customer.save()

    cart_data = cookie_cart(request)

    order: Order = Order.objects.create(customer=customer, complete=False)
    ordered_items = cart_data["ordered_items"]
    for item in ordered_items:
        ordered_item: OrderItem = OrderItem.objects.create(
            product=item["product"],
            order=order,
            quantity=item["quantity"],
        )
    return (customer, order)


def calculate_price_with_coupon(
    request, price: Decimal, coupon_code: str, *, use_coupon: bool = False
):
    """REDUNDANT METHOD: Calculate price with a coupon applied."""
    if coupon_code == "":
        return (price, "NO_COUPON")

    user: User = request.user

    status = validate_coupon(coupon_code=coupon_code, user=user)
    if status["valid"]:
        end_price: Decimal = price
        coupon: Coupon = Coupon.objects.get(code=coupon_code)
        discount: Discount = coupon.discount

        if use_coupon:
            coupon.use_coupon(user=user)

        if discount.is_percentage:
            discount_percentage: int = min(discount.value, 100)
            discount_amount: Decimal = price * discount_percentage * 0.01
        else:
            discount_amount: int = discount.value
        end_price = max(end_price - discount_amount, 0)

        return (end_price, "OK")

    # If the coupon is invalid, return the initial price and the error message
    return (price, status["message"])
