from django import forms
from .models import UserSubscription


class UserSubscriptionForm(forms.ModelForm):
    class Meta:
        model = UserSubscription
        fields = ['subscription_package']

    subscription_package = forms.ModelChoiceField(queryset=SubscriptionPackage.objects.all(), empty_label="Select a Subscription Plan")
