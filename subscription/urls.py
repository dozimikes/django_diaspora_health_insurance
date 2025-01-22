from django.urls import path
from . import views

urlpatterns = [
    path('subscriptions/', views.subscription_list, name='subscription_list'),
    path('subscriptions/<int:package_id>/', views.subscription_detail, name='subscription_detail'),
    path('subscriptions/<int:subscription_id>/checkout/', views.checkout, name='checkout'),
    path('subscriptions/<int:package_id>/checkout/', views.subscription_checkout, name='subscription_checkout'),
    path('subscriptions/<int:package_id>/create/', views.create_recurring_subscription, name='create_recurring_subscription'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),  # Callback URL for Paystack
]
