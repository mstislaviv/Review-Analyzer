import stripe
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Stripe with API key
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_placeholder")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_placeholder")

stripe.api_key = STRIPE_SECRET_KEY

# Pricing configuration
PRICING_PLANS = {
    "basic": {
        "name": "Basic Analysis",
        "price": 29.99,
        "description": "Single business review analysis"
    },
    "pro": {
        "name": "Pro Analysis",
        "price": 79.99,
        "description": "Up to 5 businesses, priority support"
    },
    "enterprise": {
        "name": "Enterprise Analysis",
        "price": 199.99,
        "description": "Unlimited businesses, dedicated support"
    }
}

def create_payment_intent(amount: float, email: str, description: str = None):
    """Create a Stripe payment intent"""
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency="usd",
            description=description or "AI Review Analysis",
            receipt_email=email,
            metadata={
                "email": email
            }
        )
        return intent
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe error: {str(e)}")

def retrieve_payment_intent(payment_intent_id: str):
    """Retrieve a payment intent"""
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return intent
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe error: {str(e)}")

def create_customer(email: str, name: str = None):
    """Create a Stripe customer"""
    try:
        customer = stripe.Customer.create(
            email=email,
            name=name or email
        )
        return customer
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe error: {str(e)}")

def get_customer(customer_id: str):
    """Get a Stripe customer"""
    try:
        customer = stripe.Customer.retrieve(customer_id)
        return customer
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe error: {str(e)}")
