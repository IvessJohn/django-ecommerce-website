import json

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
