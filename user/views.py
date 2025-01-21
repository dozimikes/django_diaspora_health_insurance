from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import User, Quote, Transaction, FamilyBeneficiary
from .forms import QuickQuoteForm, MyselfSignupForm, FamilyBeneficiaryForm
import stripe
from django.contrib.auth.decorators import login_required


stripe.api_key = settings.STRIPE_API_KEY


# Dashboard view
def dashboard(request):
    user_quotes = Quote.objects.filter(user=request.user)
    transactions = Transaction.objects.filter(user=request.user)
    return render(request, "user/dashboard.html", {"quotes": user_quotes, "transactions": transactions})


def create_payment_intent(request):
    if request.method == "POST":
        try:
            # Create a PaymentIntent with the amount to be charged
            payment_intent = stripe.PaymentIntent.create(
                amount=1000,  # Amount in cents (e.g., $10)
                currency='usd',
            )
            return JsonResponse({'client_secret': payment_intent.client_secret})
        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=400)
    return render(request, 'your_template.html')  # Replace with your actual template


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
            # Create the FamilyBeneficiary instance but don't save to DB yet
            beneficiary = form.save(commit=False)
            # Associate the beneficiary with the currently logged-in user
            beneficiary.user = request.user
            # Save the instance to the database
            beneficiary.save()
            # Redirect to dashboard after successful signup
            return redirect("dashboard")  # Ensure the 'dashboard' URL name exists in urls.py
        else:
            # If form is not valid, you can add error handling here
            # Optionally log the errors or add custom messages to the context
            print(form.errors)  # For debugging purposes, can be removed later
    else:
        form = FamilyBeneficiaryForm()  # Empty form on GET request

    return render(request, "user/family_signup.html", {"form": form})


# Checkout view
def checkout(request, quote_id):
    # Retrieve the quote based on the quote_id
    try:
        quote = Quote.objects.get(id=quote_id, user=request.user)
    except Quote.DoesNotExist:
        return render(request, "error.html", {"message": "Quote not found."})

    # If the quote has already been paid, redirect to the dashboard or a different page
    if quote.is_paid:
        return redirect('dashboard')  # Or any other page you'd like to redirect to

    if request.method == "POST":
        try:
            # Create a Stripe payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(quote.amount_paid * 100),  # Stripe expects the amount in cents
                currency="usd",  # You can adjust this to your preferred currency
                payment_method_types=["card"],  # Only cards for now
                metadata={"quote_id": quote.id, "user_id": request.user.id},
            )

            # Save transaction details in the database (set the status to Pending)
            transaction = Transaction.objects.create(
                user=request.user,
                quote=quote,
                amount=quote.amount_paid,
                payment_gateway="Stripe",
                transaction_id=intent["id"],
                status="Pending",
            )

            # Return the client secret from the Stripe payment intent so that the frontend can process the payment
            return JsonResponse({"client_secret": intent["client_secret"]})

        except stripe.error.StripeError as e:
            # Catch any Stripe-related errors and render the checkout page with the error message
            return render(request, "user/checkout.html", {"quote": quote, "error": str(e)})
        except Exception as e:
            # Catch other potential errors and return an error message
            return render(request, "user/checkout.html", {"quote": quote, "error": "An error occurred: " + str(e)})

    return render(request, "user/checkout.html", {"quote": quote})


def quick_quote(request):
    if not request.user.is_authenticated:
        # Redirect to login page if the user is not authenticated
        return redirect('login')  # Ensure 'login' URL is correctly named in your URLs

    if request.method == "POST":
        # Ensure user is a valid instance before saving to Quote
        try:
            user = request.user
            # Plan selection logic
            plan = request.POST.get('plan')
            amount_paid = None  # Default, we'll determine this from the plan

            if plan == 'Bronze':
                amount_paid = 100  # Example price for Bronze plan
            elif plan == 'Ruby':
                amount_paid = 200  # Example price for Ruby plan
            elif plan == 'Gold':
                amount_paid = 300  # Example price for Gold plan
            elif plan == 'Platinum':
                amount_paid = 400  # Example price for Platinum plan

            # Create the Quote instance
            quote = Quote.objects.create(user=user, plan=plan, amount_paid=amount_paid)
            return redirect('quote_summary')  # Redirect to a summary or confirmation page
        
        except User.DoesNotExist:
            # Handle case where the user does not exist (although it shouldn't happen if authenticated)
            return redirect('login')  # Or you can render an error page here

    return render(request, "user/quick_quote.html")


def payment_success(request):
    return render(request, 'user/payment_success.html')

def payment_cancel(request):
    return render(request, 'user/payment_cancel.html')

def create_checkout_session(request, quote_id):
    quote = Quote.objects.get(id=quote_id, user=request.user)

    if quote.is_paid:
        return redirect('dashboard')

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': quote.plan,
                },
                'unit_amount': int(quote.amount_paid * 100),  # Amount in cents
            },
            'quantity': 1,
        }],
        mode="payment",
        success_url=request.build_absolute_uri('/payment-success/'),
        cancel_url=request.build_absolute_uri('/payment-cancel/'),
    )
    
    return JsonResponse({
        'id': session.id
    })

