from django import forms
from .models import UserProfile, Quote, Transaction, FamilyBeneficiary, IdentificationDocument


class QuickQuoteForm(forms.ModelForm):
    """Form to allow users to quickly select a plan."""
    class Meta:
        model = Quote
        fields = ["plan"]
        widgets = {
            'plan': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_plan(self):
        """Optional: Add validation to ensure that the selected plan is valid."""
        plan = self.cleaned_data.get('plan')
        if plan not in ['Bronze', 'Ruby', 'Gold', 'Platinum']:
            raise forms.ValidationError("Invalid plan selected.")
        return plan


class MyselfSignupForm(forms.ModelForm):
    """Form to capture user's personal details for signup."""
    class Meta:
        model = UserProfile
        fields = [
            "address", "state", "town", "date_of_birth", "marital_status",
            "current_medical_condition", "pre_existing_conditions"
        ]
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your address'}),
            'state': forms.Select(attrs={'class': 'form-control'}),
            'town': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your town'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'marital_status': forms.Select(attrs={'class': 'form-control'}),
            'current_medical_condition': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe any current medical conditions'}),
            'pre_existing_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe any pre-existing conditions'}),
        }

    def clean_date_of_birth(self):
        """Ensure the date of birth is valid and user is at least 18 years old."""
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            from datetime import date
            age = (date.today() - dob).days // 365
            if age < 18:
                raise forms.ValidationError("You must be at least 18 years old to sign up.")
        return dob


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
            'gender': forms.Select(attrs={'class': 'form-control'}),
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

    def clean_mobile_number(self):
        """Ensure the mobile number is in a valid format."""
        mobile_number = self.cleaned_data.get('mobile_number')
        if mobile_number and len(mobile_number) < 10:
            raise forms.ValidationError("Mobile number must be at least 10 digits long.")
        return mobile_number


class IdentificationDocumentForm(forms.ModelForm):
    """Form for capturing identification documents."""
    class Meta:
        model = IdentificationDocument
        fields = ['identification_type', 'identification_number', 'identification_image', 'issue_date', 'expiry_date']
        widgets = {
            'identification_type': forms.Select(attrs={'class': 'form-control'}),
            'identification_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ID number'}),
            'identification_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean_expiry_date(self):
        """Ensure that the expiry date is not in the past."""
        expiry_date = self.cleaned_data.get('expiry_date')
        if expiry_date and expiry_date < date.today():
            raise forms.ValidationError("Expiry date cannot be in the past.")
        return expiry_date
