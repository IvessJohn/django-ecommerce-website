from math import prod
import string
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.http import JsonResponse
import json
import datetime
from decimal import Decimal

from .models import Customer, Product, Order, OrderItem, ShippingInformation

# Create your views here.
def store(request):
    ordered_items = []
    order = {"get_cart_total": 0, "get_items_amount": 0}
    items_amount = order["get_items_amount"]

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        ordered_items = order.orderitem_set.all()
        items_amount = order.get_items_amount

    products = Product.objects.all()

    context = {"products": products, "items_amount": items_amount}
    return render(request, "store/store.html", context)


def cart(request):
    ordered_items = []
    order = {"get_cart_price": 0, "get_items_amount": 0, "requires_shipping": False}
    items_amount = order["get_items_amount"]

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        ordered_items = order.orderitem_set.all()
        items_amount = order.get_items_amount
    else:
        cart = {}
        if "cart" in request.COOKIES:
            cart = json.loads(request.COOKIES["cart"])
        print("Cart:", cart)

        for i in cart:
            product: Product = Product.objects.get(id=i)
            product_quantity: int = cart[i]["quantity"]

            order["get_items_amount"] += product_quantity
            order["get_cart_price"] += product.price * product_quantity
            if not product.digital:
                order["requires_shipping"] = True
            
            ordered_item = {
                'product': product,
                'quantity': product_quantity,
                'get_total_price': product.price * product_quantity
            }
            ordered_items.append(ordered_item)

        items_amount = order["get_items_amount"]

    context = {
        "order": order,
        "ordered_items": ordered_items,
        "items_amount": items_amount,
    }
    return render(request, "store/cart.html", context)


def checkout(request):
    ordered_items = []
    order = {"get_cart_total": 0, "get_items_amount": 0}
    items_amount = order["get_items_amount"]
    requires_shipping = False

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        ordered_items = order.orderitem_set.all()

        items_amount = order.get_items_amount
        requires_shipping = order.requires_shipping
    print(f"Requires shipping: {requires_shipping}")

    context = {
        "order": order,
        "ordered_items": ordered_items,
        "items_amount": items_amount,
        "requires_shipping": requires_shipping,
    }
    return render(request, "store/checkout.html", context)


def update_item(request):
    data = json.loads(request.body)
    product_id: int = data["productId"]
    action: str = data["action"]
    print(f"deserialized json data: {product_id} {action}")

    customer = request.user.customer
    product = Product.objects.get(id=product_id)

    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == "add":
        order_item.quantity += 1
    elif action == "remove_one":
        order_item.quantity -= 1

    order_item.save()

    if order_item.quantity <= 0:
        order_item.delete()

    return JsonResponse("Item was updated", safe=False)


def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = Decimal(data["userFormData"]["total"])

        order.transaction_id = transaction_id
        if total == order.get_cart_price:
            order.complete = True
        order.save()

        if order.requires_shipping:
            ShippingInformation.objects.create(
                customer=customer,
                order=order,
                address=data["shippingInfo"]["address"],
                city=data["shippingInfo"]["city"],
                state=data["shippingInfo"]["state"],
                zipcode=data["shippingInfo"]["zipcode"],
            )
    else:
        print("User not logged in.")
    print(f"Payment data: {request.body}")
    return JsonResponse("Payment submitted...", safe=False)


def logout_view(request):
    logout(request)
    return redirect("/")
