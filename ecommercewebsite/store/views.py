from django.shortcuts import render, redirect

from .models import Customer, Product, Order, OrderItem, ShippingInformation

# Create your views here.
def store(request):
    products = Product.objects.all()

    context = {"products": products}
    return render(request, "store/store.html", context)


def cart(request):
    ordered_items = []
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        ordered_items = order.orderitem_set.all()
    
    context = {"ordered_items": ordered_items}
    return render(request, "store/cart.html", context)


def checkout(request):
    context = {}
    return render(request, "store/checkout.html", context)
