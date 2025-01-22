from django.db import models
from django.contrib.auth.models import User

# FamilyBeneficiary model
class FamilyBeneficiary(models.Model):
    # Assuming you have a ForeignKey to User for this model
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="family_beneficiaries")
    
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender_choices = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    gender = models.CharField(max_length=6, choices=gender_choices)
    relationship = models.CharField(max_length=100)
    passport_photo = models.ImageField(upload_to='passport_photos/', blank=True, null=True)
    mobile_number = models.CharField(max_length=15)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.surname} ({self.relationship})"


# Quote model
class Quote(models.Model):
    quote_number = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.quote_number

# SubscriptionPackage model
class SubscriptionPackage(models.Model):
    BRONZE = 'Bronze'
    SILVER = 'Silver'
    GOLD = 'Gold'
    PLATINUM = 'Platinum'

    PACKAGE_CHOICES = [
        (BRONZE, 'Bronze'),
        (SILVER, 'Silver'),
        (GOLD, 'Gold'),
        (PLATINUM, 'Platinum'),
    ]

    name = models.CharField(max_length=100, choices=PACKAGE_CHOICES)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.TextField()

    def __str__(self):
        return self.name
    

# models.py (Add the UserSubscription model) # Adjust the import based on your project structure

class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription_package = models.ForeignKey(SubscriptionPackage, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status_choices = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Expired', 'Expired'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='Active')

    def __str__(self):
        return f"{self.user.username} - {self.subscription_package.name}"



# UserProfile model (Extended user profile)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    identification_type = models.CharField(max_length=100)
    identification_number = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Transaction model (for payment transactions)
class Transaction(models.Model):
    SUCCESS = 'Success'
    PENDING = 'Pending'
    FAILED = 'Failed'

    STATUS_CHOICES = [
        (SUCCESS, 'Success'),
        (PENDING, 'Pending'),
        (FAILED, 'Failed'),
    ]

    transaction_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quote = models.ForeignKey(Quote, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.transaction_id
