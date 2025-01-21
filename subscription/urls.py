from django.urls import path
from . import views

urlpatterns = [
    path('', views.subscription_list, name='subscription_list'),
    path('subscription/<int:package_id>/', views.subscription_detail, name='subscription_detail'),
]
