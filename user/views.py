from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import User, Quote, Transaction, FamilyBeneficiary, IdentificationDocument
from .forms import QuickQuoteForm, MyselfSignupForm, FamilyBeneficiaryForm, IdentificationDocumentForm
import stripe
import requests

# Stripe API key
stripe.api_key = settings.STRIPE_API_KEY


# Dashboard view
@login_required
def dashboard(request):
    user_quotes = Quote.objects.filter(user=request.user)
    transactions = Transaction.objects.filter(user=request.user)
    identifications = IdentificationDocument.objects.filter(user=request.user)
    return render(
        request,
        "user/dashboard.html",
        {
            "quotes": user_quotes,
            "transactions": transactions,
            "identifications": identifications,
        },
    )


# Paystack payment initialization
@login_required
def initialize_paystack_payment(request, quote_id):
    """
    Initializes a Paystack payment by sending the quote details to Paystack's API.
    """
    try:
        quote = Quote.objects.get(id=quote_id, user=request.user)
    except Quote.DoesNotExist:
        return JsonResponse({"error": "Quote not found."}, status=404)

    if quote.is_paid:
        return JsonResponse({"message": "Quote is already paid."}, status=400)

    paystack_url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "email": request.user.email,
        "amount": int(quote.amount_paid * 100),  # Paystack expects amount in kobo
        "callback_url": request.build_absolute_uri(
            reverse("verify_paystack_payment", args=[quote.id])
        ),
    }

    response = requests.post(paystack_url, json=data, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        authorization_url = response_data["data"]["authorization_url"]
        return JsonResponse({"authorization_url": authorization_url})
    else:
        return JsonResponse({"error": "Paystack initialization failed."}, status=500)


# Paystack payment verification
@login_required
def verify_paystack_payment(request, quote_id):
    """
    Verifies a Paystack payment by checking the transaction reference.
    """
    reference = request.GET.get("reference")
    if not reference:
        return JsonResponse({"error": "Transaction reference is missing."}, status=400)

    try:
        quote = Quote.objects.get(id=quote_id, user=request.user)
    except Quote.DoesNotExist:
        return JsonResponse({"error": "Quote not found."}, status=404)

    paystack_url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    response = requests.get(paystack_url, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        if response_data["data"]["status"] == "success":
            # Mark quote as paid
            quote.is_paid = True
            quote.save()

            # Save transaction details
            Transaction.objects.create(
                user=request.user,
                quote=quote,
                amount=quote.amount_paid,
                payment_gateway="Paystack",
                transaction_id=reference,
                status="Successful",
            )

            return redirect("payment_success")
        else:
            return JsonResponse({"error": "Payment verification failed."}, status=400)
    else:
        return JsonResponse({"error": "Paystack verification failed."}, status=500)


# Stripe payment initialization
def create_payment_intent(request):
    if request.method == "POST":
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=1000,  # Amount in cents
                currency="usd",
            )
            return JsonResponse({"client_secret": payment_intent.client_secret})
        except stripe.error.StripeError as e:
            return JsonResponse({"error": str(e)}, status=400)
    return render(request, "your_template.html")  # Replace with your actual template


# Myself Signup view
def myself_signup(request):
    if request.method == "POST":
        form = MyselfSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            return redirect("dashboard")
    else:
        form = MyselfSignupForm()
    return render(request, "user/myself_signup.html", {"form": form})


# Family Signup view
def family_signup(request):
    if request.method == "POST":
        form = FamilyBeneficiaryForm(request.POST, request.FILES)
        if form.is_valid():
            beneficiary = form.save(commit=False)
            beneficiary.user = request.user
            beneficiary.save()
            return redirect("dashboard")
    else:
        form = FamilyBeneficiaryForm()
    return render(request, "user/family_signup.html", {"form": form})


# Checkout view
def checkout(request, quote_id):
    try:
        quote = Quote.objects.get(id=quote_id, user=request.user)
    except Quote.DoesNotExist:
        return render(request, "error.html", {"message": "Quote not found."})

    if quote.is_paid:
        return redirect("dashboard")

    if request.method == "POST":
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(quote.amount_paid * 100),
                currency="usd",
                payment_method_types=["card"],
                metadata={"quote_id": quote.id, "user_id": request.user.id},
            )

            transaction = Transaction.objects.create(
                user=request.user,
                quote=quote,
                amount=quote.amount_paid,
                payment_gateway="Stripe",
                transaction_id=intent["id"],
                status="Pending",
            )

            return JsonResponse({"client_secret": intent["client_secret"]})

        except stripe.error.StripeError as e:
            return render(request, "user/checkout.html", {"quote": quote, "error": str(e)})
        except Exception as e:
            return render(request, "user/checkout.html", {"quote": quote, "error": "An error occurred: " + str(e)})

    return render(request, "user/checkout.html", {"quote": quote})


# Payment Success view
def payment_success(request):
    return render(request, "user/payment_success.html")


# Payment Cancel view
def payment_cancel(request):
    return render(request, "user/payment_cancel.html")


def quick_quote(request):
    """View to allow users to quickly select a plan."""
    if request.method == "POST":
        form = QuickQuoteForm(request.POST)
        if form.is_valid():
            # Process the quote and redirect or display confirmation
            plan = form.cleaned_data['plan']
            # Logic for handling the quote selection
            return render(request, 'user/quote_success.html', {'plan': plan})
    else:
        form = QuickQuoteForm()
    
    return render(request, 'user/quick_quote.html', {'form': form})


def create_checkout_session(request, quote_id):
    """Create a checkout session for Stripe."""
    # Fetch the Quote object, assuming it has a price associated with it
    quote = Quote.objects.get(id=quote_id)

    # Create a new Stripe checkout session
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',  # You can replace with dynamic currency
                    'product_data': {
                        'name': f"Subscription: {quote.plan}",
                    },
                    'unit_amount': int(quote.amount_paid * 100),  # Amount in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/payment-success/'),
            cancel_url=request.build_absolute_uri('/payment-cancel/'),
        )
        return JsonResponse({
            'id': checkout_session.id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

