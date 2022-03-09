import string
from django.shortcuts import render, redirect
from django.http import JsonResponse
import json

from .models import Customer, Product, Order, OrderItem, ShippingInformation

# Create your views here.
def store(request):
    products = Product.objects.all()

    context = {"products": products}
    return render(request, "store/store.html", context)


def cart(request):
    ordered_items = []
    order = {'get_cart_total': 0, 'get_items_amount': 0}

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        ordered_items = order.orderitem_set.all()
    
    context = {"order": order, "ordered_items": ordered_items}
    return render(request, "store/cart.html", context)


def checkout(request):
    ordered_items = []
    order = {'get_cart_total': 0, 'get_items_amount': 0}

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        ordered_items = order.orderitem_set.all()
    
    context = {"order": order, "ordered_items": ordered_items}
    return render(request, "store/checkout.html", context)


def update_item(request):
    data = json.loads(request.body)
    product_id: int = data['productId']
    action: str = data['action']
    print(f'deserialized json data: {product_id} {action}')

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