from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class SubscriptionPackage(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price without discount
    is_yearly = models.BooleanField(default=False)  # If True, it's a yearly plan

    def __str__(self):
        return self.name

    def get_discounted_price(self):
        # Apply a 20% discount for yearly plans
        if self.is_yearly:
            return self.price * 0.8
        return self.price


class Transaction(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed"),
        ("Refunded", "Refunded"),
    ]

    PAYMENT_GATEWAY_CHOICES = [
        ("Stripe", "Stripe"),
        ("Paystack", "Paystack"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    subscription_package = models.ForeignKey(
        SubscriptionPackage,  # Direct reference to the model
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    payment_gateway = models.CharField(max_length=50, choices=PAYMENT_GATEWAY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_id} - {self.status}"


class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(SubscriptionPackage, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    transaction_id = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if self.package.is_yearly:
            # For yearly plans, set the end date to one year later
            self.end_date = self.start_date.replace(year=self.start_date.year + 1)
        else:
            # For monthly plans, set the end date to one month later
            month = self.start_date.month + 1
            year = self.start_date.year
            if month > 12:
                month -= 12
                year += 1
            self.end_date = self.start_date.replace(year=year, month=month)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.package.name}"
