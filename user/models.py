from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    # Custom related_name for groups and user_permissions to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True
    )

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    town = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    marital_status = models.CharField(
        max_length=20,
        choices=[("Single", "Single"), ("Married", "Married"), ("Widowed", "Widowed"), ("Divorced", "Divorced")],
        blank=True,
        null=True
    )
    current_medical_condition = models.BooleanField(default=False)
    pre_existing_conditions = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class IdentificationDocument(models.Model):
    IDENTIFICATION_TYPE_CHOICES = [
        ("Passport", "Passport"),
        ("Driver's License", "Driver's License"),
        ("National ID Card", "National ID Card"),
        ("Voter ID", "Voter ID"),
        ("Social Security Card", "Social Security Card"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='identifications')
    identification_type = models.CharField(max_length=50, choices=IDENTIFICATION_TYPE_CHOICES)
    identification_number = models.CharField(max_length=100)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    identification_image = models.ImageField(upload_to='identifications/', null=True, blank=True)

    def __str__(self):
        return f"{self.identification_type} - {self.user.username}"


class Quote(models.Model):
    PLAN_CHOICES = [
        ("Bronze", "Bronze"),
        ("Ruby", "Ruby"),
        ("Gold", "Gold"),
        ("Platinum", "Platinum"),
    ]

    PLAN_PRICES = {
        "Bronze": 100.00,
        "Ruby": 200.00,
        "Gold": 300.00,
        "Platinum": 400.00,
    }

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    plan = models.CharField(max_length=50, choices=PLAN_CHOICES)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.amount_paid:
            self.amount_paid = self.PLAN_PRICES.get(self.plan, 0.00)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.plan} - {self.user.username if self.user else 'Anonymous'}"


class Transaction(models.Model):
    PAYMENT_GATEWAY_CHOICES = [
        ("Stripe", "Stripe"),
        ("Paystack", "Paystack"),
    ]

    STATUS_CHOICES = [
        ("Success", "Success"),
        ("Pending", "Pending"),
        ("Failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quote = models.ForeignKey(Quote, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_gateway = models.CharField(max_length=50, choices=PAYMENT_GATEWAY_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    paystack_reference = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.payment_gateway} - ${self.amount}"


class FamilyBeneficiary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female")])
    date_of_birth = models.DateField()
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    passport_photo = models.ImageField(upload_to='beneficiary_photos/', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.surname} - {self.relationship}"
