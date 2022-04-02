import json
import datetime
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login

from django_countries import Countries

from .models import Customer, Product, Order, OrderItem, ShippingInformation
from . import utils
from .forms import CreateUserForm

# Create your views here.
#region Authentication
def register_view(request) -> HttpResponse:
    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user: User = form.save()
            username = user.username

            # messages.success(request, f"Account for {username} was created successfully!")

            return redirect("login")

    context = {
        "form": form,
    }
    return render(request, "store/register.html", context)


def login_view(request) -> HttpResponse:
    if request.method == "POST":
        _username = request.POST.get("username")
        _password = request.POST.get("password")

        user = authenticate(request.POST, username=_username, password=_password)

        # if user:
        if user is not None:
            login(request, user)
            return redirect("store")
        else:
            # messages.info(request, 'Username or password is incorrect.')
            pass

    context = {}
    return render(request, "store/login.html", context)


def logout_view(request) -> HttpResponse:
    """Logout."""
    logout(request)
    return redirect("/")

#endregion


#region Store pages rendering
def store(request) -> HttpResponse:
    order_data = utils.get_order_data(request)
    items_amount = order_data["items_amount"]

    products = Product.objects.all()

    context = {"products": products, "items_amount": items_amount}
    return render(request, "store/store.html", context)


def cart(request) -> HttpResponse:
    order_data = utils.get_order_data(request)
    order = order_data["order"]
    ordered_items = order_data["ordered_items"]
    items_amount = order_data["items_amount"]

    context = {
        "order": order,
        "ordered_items": ordered_items,
        "items_amount": items_amount,
    }
    return render(request, "store/cart.html", context)


def checkout(request) -> HttpResponse:
    order_data = utils.get_order_data(request)
    order = order_data["order"]
    ordered_items = order_data["ordered_items"]
    items_amount = order_data["items_amount"]
    requires_shipping = order_data["requires_shipping"]

    context = {
        "order": order,
        "ordered_items": ordered_items,
        "items_amount": items_amount,
        "requires_shipping": requires_shipping,
        "countries": Countries,
    }
    return render(request, "store/checkout.html", context)

#endregion


#region AJAX
def update_item(request) -> JsonResponse:
    """Update order item quantity within the database.
    The modified order item is retrieved using the information sent from the front-end."""
    data = json.loads(request.body)
    product_id: int = data["productId"]
    action: str = data["action"]
    # print(f"deserialized json data: {product_id} {action}")

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

    response: dict = {
        "ordered_item_quantity": order_item.quantity,
        "total_items": order.get_items_amount,
    }
    return JsonResponse(json.dumps(response), safe=False)


def process_order(request) -> JsonResponse:
    """Process an order.
    Set a timestamp for it. If the prices on the front end and on the back end are
    equal, mark the order as complete.
    """
    data = json.loads(request.body)

    # Create/Get the current order
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = utils.create_guest_order(request, data)

    # Save shipping information if the order requires shipping
    if order.requires_shipping:
        ShippingInformation.objects.create(
            customer=customer,
            order=order,
            address=data["shippingInfo"]["address"],
            city=data["shippingInfo"]["city"],
            state=data["shippingInfo"]["state"],
            zipcode=data["shippingInfo"]["zipcode"],
            country=data["shippingInfo"]["country"],
        )

    # Set the transaction ID
    transaction_id = datetime.datetime.now().timestamp()
    order.transaction_id = transaction_id

    # Check price
    total = Decimal(data["userFormData"]["total"])
    if total == order.get_final_price:
        order.complete = True
    order.save()

    print(f"Payment data: {request.body}")
    return JsonResponse("Payment submitted...", safe=False)


def apply_coupon(request) -> JsonResponse:
    data = json.loads(request.body)
    coupon_code = data["couponCode"]

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        order.apply_coupon(coupon_code)

    return JsonResponse("Coupon applied...", safe=False)


def get_order(request) -> JsonResponse:
    order_data = utils.get_order_data(request)
    return JsonResponse(json.dumps(order_data))


# endregion

#region Other
def about_page(request) -> HttpResponse:
    context = {}
    return render(request, "store/about.html", context)
#endregion