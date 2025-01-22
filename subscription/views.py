from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import SubscriptionPackage, UserSubscription, Transaction
from django.http import JsonResponse, HttpResponse
from .models import Transaction, Quote
import logging
from .forms import UserSubscriptionForm
import stripe
import requests
from django.conf import settings


# Set up logging
logger = logging.getLogger(__name__)

# Set your Stripe secret key
stripe.api_key = settings.STRIPE_API_KEY

# Paystack API details
PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
PAYSTACK_API_URL = "https://api.paystack.co/transaction/initialize"


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


def checkout(request, subscription_id):
    subscription = UserSubscription.objects.get(id=subscription_id)
    if request.method == "POST":
        payment_method = request.POST.get('payment_method')  # Paystack or Stripe
        amount = subscription.subscription_package.price if subscription.subscription_package else 0

        # Handle Paystack payment
        if payment_method == "paystack":
            try:
                # Initialize Paystack transaction
                headers = {
                    'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}',
                    'Content-Type': 'application/json',
                }

                data = {
                    "email": request.user.email,
                    "amount": int(amount * 100),  # Paystack processes amounts in kobo
                    "currency": "NGN",
                    "callback_url": request.build_absolute_uri('/payment/callback/'),  # Your callback URL after payment
                    "metadata": {"subscription_id": subscription.id, "user_id": request.user.id},
                }

                response = requests.post(PAYSTACK_API_URL, json=data, headers=headers)
                response_data = response.json()

                if response_data["status"]:
                    authorization_url = response_data["data"]["authorization_url"]

                    # Save transaction with status Pending for Paystack
                    Transaction.objects.create(
                        user=request.user,
                        subscription_package=subscription.subscription_package,
                        amount=amount,
                        payment_gateway="Paystack",
                        transaction_id=response_data["data"]["reference"],
                        status="Pending",
                    )

                    return JsonResponse({"authorization_url": authorization_url})

                return JsonResponse({"error": "Unable to initialize Paystack payment."}, status=400)
            except requests.exceptions.RequestException as e:
                return render(request, "payments/checkout.html", {"subscription": subscription, "error": str(e)})

        # Handle Stripe payment
        elif payment_method == "stripe":
            try:
                # Create Stripe payment intent
                intent = stripe.PaymentIntent.create(
                    amount=int(amount * 100),  # Stripe processes amounts in cents
                    currency="usd",
                    payment_method_types=["card"],
                    metadata={"subscription_id": subscription.id, "user_id": request.user.id},
                )

                # Save transaction
                Transaction.objects.create(
                    user=request.user,
                    subscription_package=subscription.subscription_package,
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
        payment_method = request.POST.get('payment_method')  # Paystack or Stripe

        # Handle Paystack payment
        if payment_method == "paystack":
            try:
                # Initialize Paystack transaction
                headers = {
                    'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}',
                    'Content-Type': 'application/json',
                }

                data = {
                    "email": request.user.email,
                    "amount": int(discounted_price * 100),  # Paystack processes amounts in kobo
                    "currency": "NGN",
                    "callback_url": request.build_absolute_uri('/payment/callback/'),  # Your callback URL after payment
                    "metadata": {"package_id": package.id, "user_id": request.user.id},
                }

                response = requests.post(PAYSTACK_API_URL, json=data, headers=headers)
                response_data = response.json()

                if response_data["status"]:
                    authorization_url = response_data["data"]["authorization_url"]

                    # Save subscription with the user
                    UserSubscription.objects.create(
                        user=request.user,
                        subscription_package=package,
                        transaction_id=response_data["data"]["reference"],
                        is_active=True,
                    )

                    return JsonResponse({"authorization_url": authorization_url})

                return JsonResponse({"error": "Unable to initialize Paystack payment."}, status=400)
            except requests.exceptions.RequestException as e:
                return render(request, "subscriptions/subscription_checkout.html", {"error": str(e)})

        # Handle Stripe payment
        elif payment_method == "stripe":
            try:
                # Create Stripe payment intent
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
                    subscription_package=package,
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


def create_recurring_subscription(request, package_id):
    package = SubscriptionPackage.objects.get(id=package_id)

    # Apply discount for yearly subscription
    if package.is_yearly:
        discounted_price = package.price * 0.8
    else:
        discounted_price = package.price

    # Handle Paystack payment
    if request.method == "POST" and request.POST.get('payment_method') == "paystack":
        try:
            # Initialize Paystack transaction
            headers = {
                'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}',
                'Content-Type': 'application/json',
            }

            data = {
                "email": request.user.email,
                "amount": int(discounted_price * 100),  # Paystack processes amounts in kobo
                "currency": "NGN",
                "callback_url": request.build_absolute_uri('/payment/callback/'),  # Your callback URL after payment
                "metadata": {"package_id": package.id, "user_id": request.user.id},
            }

            response = requests.post(PAYSTACK_API_URL, json=data, headers=headers)
            response_data = response.json()

            if response_data["status"]:
                authorization_url = response_data["data"]["authorization_url"]

                # Save subscription with the user
                UserSubscription.objects.create(
                    user=request.user,
                    subscription_package=package,
                    transaction_id=response_data["data"]["reference"],
                    is_active=True,
                )

                return JsonResponse({"authorization_url": authorization_url})

            return JsonResponse({"error": "Unable to initialize Paystack payment."}, status=400)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": str(e)})

    return JsonResponse({"status": "Subscription created successfully!"})


@login_required
def payment_callback(request):
    """Handle payment callback from payment gateway."""
    if request.method == "POST":
        # Get payment gateway response data (e.g., from Stripe or Paystack)
        payment_status = request.POST.get('status')  # Assuming 'status' is a field in the POST data
        transaction_id = request.POST.get('transaction_id')  # Assuming 'transaction_id' is part of the response
        payment_gateway = request.POST.get('payment_gateway')  # Payment gateway name (Stripe/Paystack)
        quote_id = request.POST.get('quote_id')  # The related quote ID
        transaction_reference = request.POST.get('reference')  # Example, adjust based on your gateway
        
        # Log the received data
        logger.info(f"Payment callback received from {payment_gateway}. Transaction ID: {transaction_id}")
        
        # Fetch the related transaction record
        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)
        except Transaction.DoesNotExist:
            logger.error(f"Transaction {transaction_id} not found.")
            return HttpResponse(status=400)  # Bad request if transaction not found
        
        # Check the payment status and update the transaction record
        if payment_status == 'success':
            transaction.status = 'Success'
            # Update quote as paid
            if quote_id:
                try:
                    quote = Quote.objects.get(id=quote_id)
                    quote.is_paid = True
                    quote.save()
                except Quote.DoesNotExist:
                    logger.error(f"Quote with ID {quote_id} not found.")
                    return HttpResponse(status=400)
        else:
            transaction.status = 'Failed'
        
        transaction.save()
        
        # Optionally, you can send a success response
        return JsonResponse({'status': 'success'}, status=200)

    else:
        return HttpResponse(status=405)  # Method Not Allowed for non-POST requests
