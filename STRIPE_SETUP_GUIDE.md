# Stripe Payment Integration Setup Guide

## Overview
This guide explains how to set up Stripe payments for the AI Review Analyzer application.

## What's Included

### New Features
- ✅ Stripe payment processing
- ✅ Payment intent creation
- ✅ Webhook handling for payment events
- ✅ Checkout page with Stripe Elements
- ✅ Payment success/failure pages
- ✅ Payment history tracking

### New Database Tables
- **payments**: Stores payment records with Stripe integration
- **Updated users**: Added `stripe_customer_id` field
- **Updated orders**: Added `price` and `payment_id` fields

### New Files Created
- `app/stripe_config.py` - Stripe configuration and utilities
- `app/templates/checkout.html` - Checkout page with Stripe Elements
- `app/templates/payment-success.html` - Success page
- `app/templates/payment-failed.html` - Failure page

### Updated Files
- `app/models.py` - Added Payment model and Stripe fields
- `app/main.py` - Added payment routes
- `app/templates/pricing.html` - Added checkout buttons
- `requirements.txt` - Added stripe==10.0.0

## Step 1: Get Stripe API Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Sign up or log in to your Stripe account
3. Navigate to **Developers** → **API Keys**
4. You'll see two keys:
   - **Publishable Key** (starts with `pk_`)
   - **Secret Key** (starts with `sk_`)

### Test vs Live Keys
- **Test Keys**: Use for development (start with `pk_test_` and `sk_test_`)
- **Live Keys**: Use for production (start with `pk_live_` and `sk_live_`)

## Step 2: Set Environment Variables

### Local Development
Create a `.env` file in the project root:

```bash
# Stripe Keys (Test)
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY
STRIPE_WEBHOOK_SECRET=whsec_test_YOUR_WEBHOOK_SECRET

# Database
PGUSER=sandbox
PGPASSWORD=your_password
PGDATABASE=ai_review_analyzer_fastapi
```

### Production (Render)
1. Go to your Render service dashboard
2. Click **Environment**
3. Add the following variables:
   - `STRIPE_PUBLISHABLE_KEY` = Your live publishable key
   - `STRIPE_SECRET_KEY` = Your live secret key
   - `STRIPE_WEBHOOK_SECRET` = Your webhook secret

## Step 3: Set Up Webhooks

Webhooks allow Stripe to notify your application about payment events.

### Local Development (Testing)
1. Install Stripe CLI: https://stripe.com/docs/stripe-cli
2. Run: `stripe listen --forward-to localhost:8000/webhook/stripe`
3. Copy the webhook signing secret (starts with `whsec_`)
4. Add to `.env`: `STRIPE_WEBHOOK_SECRET=whsec_...`

### Production (Render)
1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Navigate to **Developers** → **Webhooks**
3. Click **Add endpoint**
4. Endpoint URL: `https://your-render-url.onrender.com/webhook/stripe`
5. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
6. Copy the signing secret and add to Render environment variables

## Step 4: Update Database

Run the database initialization script to create new tables:

```bash
# Local
python3 init_db.py

# Production (Render Shell)
python3 init_db.py
```

## Step 5: Test the Integration

### Local Testing
1. Start the application: `uvicorn app.main:app --reload`
2. Visit: http://localhost:8000/pricing
3. Click "Start Analysis" on any plan
4. Use Stripe test card: `4242 4242 4242 4242`
5. Expiry: Any future date (e.g., 12/25)
6. CVC: Any 3 digits (e.g., 123)

### Test Cards
- **Success**: 4242 4242 4242 4242
- **Decline**: 4000 0000 0000 0002
- **Requires Authentication**: 4000 0025 0000 3155

## Pricing Plans

The application includes three pricing tiers:

### Basic - $29.99
- Single business review analysis
- AI-powered insights
- PDF report generation
- Email support
- 24-hour turnaround

### Pro - $79.99
- Up to 5 business analyses
- Advanced AI insights
- Detailed PDF reports
- Priority email support
- Competitor analysis
- Trend tracking
- 12-hour turnaround

### Enterprise - $199.99
- Unlimited business analyses
- Premium AI insights
- Custom branded reports
- 24/7 phone & email support
- API access
- Custom integrations
- Dedicated account manager
- Priority processing

## Payment Flow

1. **User selects plan** → Clicks "Start Analysis"
2. **Checkout page** → User enters business details and card info
3. **Payment intent created** → Backend creates Stripe PaymentIntent
4. **Card charged** → Stripe processes the payment
5. **Order created** → Backend creates order record
6. **Success page** → User sees confirmation
7. **Webhook received** → Stripe notifies backend of payment status

## API Endpoints

### POST `/api/create-payment-intent`
Creates a Stripe PaymentIntent for the selected plan.

**Request:**
```json
{
  "plan": "basic"  // or "pro", "enterprise"
}
```

**Response:**
```json
{
  "clientSecret": "pi_..._secret_...",
  "paymentIntentId": "pi_..."
}
```

### POST `/api/confirm-payment`
Confirms payment and creates the order.

**Request:**
```json
{
  "paymentIntentId": "pi_...",
  "businessName": "Joe's Pizza Restaurant",
  "businessAddress": "123 Main Street, New York, NY 10001"
}
```

**Response:**
```json
{
  "success": true,
  "orderId": 123,
  "message": "Payment successful! Your order has been created."
}
```

### POST `/webhook/stripe`
Receives webhook events from Stripe.

**Events handled:**
- `payment_intent.succeeded` - Updates payment status to "succeeded"
- `payment_intent.payment_failed` - Updates payment status to "failed"

## Database Schema

### payments table
```sql
CREATE TABLE payments (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  stripe_payment_intent_id VARCHAR UNIQUE NOT NULL,
  stripe_charge_id VARCHAR,
  amount FLOAT NOT NULL,
  currency VARCHAR DEFAULT 'usd',
  status VARCHAR DEFAULT 'pending',
  description VARCHAR,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Updated users table
```sql
ALTER TABLE users ADD COLUMN stripe_customer_id VARCHAR UNIQUE;
```

### Updated orders table
```sql
ALTER TABLE orders ADD COLUMN price FLOAT DEFAULT 29.99;
ALTER TABLE orders ADD COLUMN payment_id INTEGER REFERENCES payments(id);
```

## Troubleshooting

### "Invalid API Key"
- Check that your Stripe keys are correct
- Ensure you're using test keys for development
- Verify keys are set in environment variables

### "Webhook signature verification failed"
- Ensure webhook secret is correct
- Check that webhook is configured in Stripe dashboard
- Verify endpoint URL is correct

### "Payment intent not found"
- Check that payment was created successfully
- Verify payment_intent_id is correct
- Check database for payment record

### "Card declined"
- Use test card: 4242 4242 4242 4242
- Check card expiry date
- Verify CVC is 3 digits

## Security Best Practices

✅ **Always use HTTPS** in production
✅ **Never log sensitive data** (API keys, card numbers)
✅ **Validate webhook signatures** (already implemented)
✅ **Use HTTP-only cookies** for tokens (already implemented)
✅ **Store only Stripe IDs** in database (no card data)
✅ **Use Stripe Elements** for card input (already implemented)

## Next Steps

1. ✅ Get Stripe API keys
2. ✅ Set environment variables
3. ✅ Set up webhooks
4. ✅ Update database
5. ✅ Test with test cards
6. ✅ Deploy to production
7. ✅ Switch to live keys
8. ✅ Monitor payments in Stripe dashboard

## Support

For Stripe documentation: https://stripe.com/docs
For API reference: https://stripe.com/docs/api
For webhook events: https://stripe.com/docs/webhooks

## Files Modified

- `app/models.py` - Added Payment model
- `app/main.py` - Added payment routes
- `app/stripe_config.py` - New Stripe utilities
- `app/templates/checkout.html` - New checkout page
- `app/templates/payment-success.html` - New success page
- `app/templates/payment-failed.html` - New failure page
- `app/templates/pricing.html` - Updated with checkout buttons
- `requirements.txt` - Added stripe dependency
- `init_db.py` - Updated for new tables

## Version Info

- Stripe API Version: 10.0.0
- Python: 3.10+
- FastAPI: 0.115.0
- SQLAlchemy: 2.0.36

---

Last Updated: October 15, 2025
Status: Ready for Integration ✅
