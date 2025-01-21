from django import forms
from .models import UserProfile, Quote, Transaction, FamilyBeneficiary

class QuickQuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ["plan"]

class MyselfSignupForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "address", "state", "town", "date_of_birth", "marital_status",
            "identification_type", "identification_number", "identification_image",
            "current_medical_condition", "pre_existing_conditions"
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'identification_image': forms.ClearableFileInput(),
        }

class FamilyBeneficiaryForm(forms.ModelForm):
    class Meta:
        model = FamilyBeneficiary
        fields = [
            "first_name", "surname", "relationship", "gender",
            "date_of_birth", "mobile_number", "passport_photo"
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'passport_photo': forms.ClearableFileInput(),
        }