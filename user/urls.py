from django.urls import path
from .views import quick_quote, myself_signup, checkout, dashboard, family_signup
from . import views


urlpatterns = [
    path("quick-quote/", quick_quote, name="quick_quote"),
    path("myself-signup/", myself_signup, name="myself_signup"),
    path("family-signup/", family_signup, name="family_signup"),
    path("checkout/<int:quote_id>/", checkout, name="checkout"),
    path("dashboard/", dashboard, name="dashboard"),
    path('checkout/<int:quote_id>/', views.checkout, name='checkout'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
    path('create-checkout-session/<int:quote_id>/', views.create_checkout_session, name='create-checkout-session'),
]