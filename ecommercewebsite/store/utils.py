import json
from decimal import Decimal

from coupon_management.validations import validate_coupon
from coupon_management.models import Coupon, Discount

from .models import *


def get_order_data(request) -> dict:
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        ordered_items = order.orderitem_set.all()
        items_amount = order.get_items_amount
        requires_shipping = order.requires_shipping
    else:
        cart_data = cookie_cart(request)
        ordered_items = cart_data['ordered_items']
        order = cart_data['order']
        items_amount = cart_data['items_amount']
        requires_shipping = cart_data['requires_shipping']

    return {
        "order": order,
        "ordered_items": ordered_items,
        "items_amount": items_amount,
        "requires_shipping": requires_shipping,
    }


def cookie_cart(request) -> dict:
    ordered_items = []
    order = {"get_cart_price": 0, "get_items_amount": 0, "requires_shipping": False}
    items_amount = order["get_items_amount"]
    cart = {}

    if "cart" in request.COOKIES:
        cart = json.loads(request.COOKIES["cart"])

    for i in cart:
        if Product.objects.filter(id=i).exists():
            product: Product = Product.objects.get(id=i)
            product_quantity: int = cart[i]["quantity"]

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

    return {
        "ordered_items": ordered_items,
        "order": order,
        "items_amount": items_amount,
        "requires_shipping": order["requires_shipping"],
    }


def create_guest_order(request, data) -> tuple[Customer, Order]:
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

def use_coupon_view(request, coupon_code, *args, **kwargs) -> str:
    user = request.user
    
    status = validate_coupon(coupon_code=coupon_code, user=user)
    if status['valid']:
        coupon = Coupon.objects.get(code=coupon_code)
        coupon.use_coupon(user=user)
    
        return "OK"
    
    return status['message']

def calculate_price_with_coupon(request, price, coupon_code):
    if coupon_code == "":
        return (price, "")
    
    end_price: Decimal = price

    error: str = use_coupon_view(request, coupon_code)
    if error == "OK":
        discount: Discount = Coupon.objects.get(code=coupon_code).discount
        if discount.is_percentage:
            discount_percentage: int = min(discount.value, 100)
            discount_amount: Decimal = price * discount_percentage * 0.01
        else:
            discount_amount: int = discount.value
        end_price = max(end_price - discount_amount, 0)

    return (end_price, error)