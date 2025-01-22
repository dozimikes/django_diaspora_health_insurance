from django import forms
from .models import UserSubscription, SubscriptionPackage, FamilyBeneficiary

class FamilyBeneficiaryForm(forms.ModelForm):
    """Form to add family beneficiaries."""
    class Meta:
        model = FamilyBeneficiary
        fields = [
            "first_name", "surname", "relationship", "gender",
            "date_of_birth", "mobile_number", "passport_photo"
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'surname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter surname'}),
            'relationship': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),  # Gender dropdown
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter mobile number'}),
            'passport_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_date_of_birth(self):
        """Validate that the beneficiary's age is reasonable (e.g., not in the future)."""
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            from datetime import date
            if dob > date.today():
                raise forms.ValidationError("Date of birth cannot be in the future.")
        return dob


class UserSubscriptionForm(forms.ModelForm):
    """Form for User Subscription."""
    class Meta:
        model = UserSubscription
        fields = ['subscription_package']

    subscription_package = forms.ModelChoiceField(
        queryset=SubscriptionPackage.objects.all(),
        empty_label="Select a Subscription Plan",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
