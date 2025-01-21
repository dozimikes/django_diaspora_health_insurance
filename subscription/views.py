from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import SubscriptionPackage, UserSubscription, Transaction
from .forms import UserSubscriptionForm
import stripe
from django.conf import settings



@login_required
def subscription_list(request):
    subscription_packages = SubscriptionPackage.objects.all()
    return render(request, "subscriptions/subscription_list.html", {"subscription_packages": subscription_packages})

@login_required
def subscription_detail(request, package_id):
    subscription_package = SubscriptionPackage.objects.get(id=package_id)

    if request.method == "POST":
        form = UserSubscriptionForm(request.POST)
        if form.is_valid():
            user_subscription = form.save(commit=False)
            user_subscription.user = request.user
            user_subscription.subscription_package = subscription_package
            user_subscription.save()

            return redirect("checkout", subscription_id=user_subscription.id)

    else:
        form = UserSubscriptionForm()

    return render(request, "subscriptions/subscription_detail.html", {
        "subscription_package": subscription_package,
        "form": form
    })


stripe.api_key = settings.STRIPE_API_KEY

def checkout(request, subscription_id):
    subscription = UserSubscription.objects.get(id=subscription_id)
    if request.method == "POST":
        try:
            # Create Stripe payment intent
            amount = subscription.subscription_package.monthly_price if subscription.subscription_package else 0
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Stripe processes amounts in cents
                currency="usd",
                payment_method_types=["card"],
                metadata={"subscription_id": subscription.id, "user_id": request.user.id},
            )

            # Save transaction
            Transaction.objects.create(
                user=request.user,
                subscription=subscription,
                amount=amount,
                payment_gateway="Stripe",
                transaction_id=intent["id"],
                status="Pending",
            )

            return JsonResponse({"client_secret": intent["client_secret"]})
        except stripe.error.StripeError as e:
            return render(request, "payments/checkout.html", {"subscription": subscription, "error": str(e)})

    return render(request, "payments/checkout.html", {"subscription": subscription})


def subscription_checkout(request, package_id):
    # Get the selected package
    package = SubscriptionPackage.objects.get(id=package_id)
    
    # Fetch the discounted price using model logic
    discounted_price = package.get_discounted_price()

    if request.method == "POST":
        try:
            # Create Stripe payment intent with future usage setup for auto-debit
            intent = stripe.PaymentIntent.create(
                amount=int(discounted_price * 100),  # Stripe processes amounts in cents
                currency="usd",
                payment_method_types=["card"],
                setup_future_usage="off_session",  # Save the card for future payments
                metadata={"package_id": package.id, "user_id": request.user.id},
            )

            # Save subscription with the user
            subscription = UserSubscription.objects.create(
                user=request.user,
                package=package,
                transaction_id=intent["id"],
                is_active=True,
            )

            return JsonResponse({"client_secret": intent["client_secret"]})

        except stripe.error.StripeError as e:
            return render(request, "subscriptions/subscription_checkout.html", {"error": str(e)})

    return render(
        request, 
        "subscriptions/subscription_checkout.html", 
        {"package": package, "discounted_price": discounted_price}
    )


# subscriptions/views.py

def create_recurring_subscription(request, package_id):
    package = SubscriptionPackage.objects.get(id=package_id)

    # Apply discount for yearly subscription
    if package.is_yearly:
        discounted_price = package.price * 0.8
    else:
        discounted_price = package.price

    # Create a Stripe subscription with saved payment method
    try:
        subscription = stripe.Subscription.create(
            customer=request.user.stripe_customer_id,
            items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': package.name,
                        },
                        'unit_amount': int(discounted_price * 100),  # Stripe processes in cents
                    },
                    'quantity': 1,
                },
            ],
            off_session=True,
            billing_cycle_anchor="now",  # Start the cycle immediately
            expand=["latest_invoice.payment_intent"],
        )

        # Save the subscription to the database
        UserSubscription.objects.create(
            user=request.user,
            package=package,
            transaction_id=subscription["latest_invoice"]["payment_intent"]["id"],
            is_active=True,
        )

        return JsonResponse({"status": "Subscription created successfully!"})

    except stripe.error.StripeError as e:
        return JsonResponse({"error": str(e)})


