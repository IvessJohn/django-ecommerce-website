from django.urls import path
from . import views


urlpatterns = [
    # Authentication-related URLs
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # Main URLs
    path("", views.store, name="store"),
    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    # Utility URLs
    path("get_order/", views.get_order, name="get_order"),
    path("update_item/", views.update_item, name="update_item"),
    path("process_order/", views.process_order, name="process_order"),
    path("apply_coupon/", views.apply_coupon, name="apply_coupon"),
]
