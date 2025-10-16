from datetime import datetime
import uuid
from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.auth import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    get_current_user_from_cookie,
    require_auth,
    validate_password,
    decode_token
)
from app.auth_db import (
    get_user_by_email,
    get_user_by_id,
    create_user,
    user_exists,
    get_user_orders
)
from app.stripe_config import STRIPE_PUBLISHABLE_KEY

app = FastAPI(title="AI Review Analyzer")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = None
    try:
        token = request.cookies.get("access_token")
        if token:
            payload = decode_token(token)
            if payload:
                email = payload.get("sub")
                if email:
                    db = next(get_db())
                    try:
                        user = get_user_by_email(db, email)
                    finally:
                        db.close()
    except:
        pass
    
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/pricing", response_class=HTMLResponse)
async def pricing(request: Request):
    user = None
    try:
        token = request.cookies.get("access_token")
        if token:
            payload = decode_token(token)
            if payload:
                email = payload.get("sub")
                if email:
                    db = next(get_db())
                    try:
                        user = get_user_by_email(db, email)
                    finally:
                        db.close()
    except:
        pass
    
    return templates.TemplateResponse("pricing.html", {"request": request, "user": user})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "user": None})

@app.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Validate inputs
        if not email or not email.strip():
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Please enter your email address", "user": None}
            )
        
        if not password:
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Please enter your password", "user": None}
            )
        
        # Find user by email
        email_lower = email.strip().lower()
        user = get_user_by_email(db, email_lower)
        
        if not user or not verify_password(password, user.password):
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Invalid email or password", "user": None}
            )
        
        # Create token and redirect
        token = create_access_token({"sub": user.email})
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="access_token", value=token, httponly=True, secure=True, samesite="lax")
        return response
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "An error occurred during login. Please try again.", "user": None}
        )

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request, "user": None})

@app.post("/signup")
async def signup(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Validate inputs
        if not name or not name.strip():
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error": "Please enter your name", "user": None}
            )
        
        if not email or not email.strip():
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error": "Please enter your email address", "user": None}
            )
        
        # Validate email format
        if "@" not in email or "." not in email:
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error": "Please enter a valid email address", "user": None}
            )
        
        # Validate password
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error": error_msg, "user": None}
            )
        
        # Check if user already exists
        email_lower = email.strip().lower()
        if user_exists(db, email_lower):
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error": "An account with this email already exists", "user": None}
            )
        
        # Create new user
        try:
            new_user = create_user(db, name.strip(), email_lower, password)
            
            # Auto login
            token = create_access_token({"sub": new_user.email})
            response = RedirectResponse(url="/dashboard", status_code=303)
            response.set_cookie(key="access_token", value=token, httponly=True, secure=True, samesite="lax")
            return response
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error": "Error creating account. Please try again.", "user": None}
            )
        
    except Exception as e:
        print(f"Signup error: {str(e)}")
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "An error occurred during signup. Please try again.", "user": None}
        )

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # Get token from cookie
        token = request.cookies.get("access_token")
        if not token:
            return RedirectResponse(url="/login", status_code=303)
        
        # Decode token
        payload = decode_token(token)
        if not payload:
            return RedirectResponse(url="/login", status_code=303)
        
        email = payload.get("sub")
        if not email:
            return RedirectResponse(url="/login", status_code=303)
        
        # Get user from database
        user = get_user_by_email(db, email)
        if not user:
            return RedirectResponse(url="/login", status_code=303)
        
        # Get user's orders
        orders = get_user_orders(db, user.id)
        
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "user": user, "orders": orders}
        )
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        return RedirectResponse(url="/login", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response

# Stripe payment routes
@app.get("/checkout", response_class=HTMLResponse)
async def checkout(request: Request, plan: str = "basic", db: Session = Depends(get_db)):
    user = None
    try:
        token = request.cookies.get("access_token")
        if token:
            payload = decode_token(token)
            if payload:
                email = payload.get("sub")
                if email:
                    user = get_user_by_email(db, email)
    except:
        pass
    
    # Pricing plans
    plans = {
        "basic": {
            "name": "Basic",
            "price": 29.99,
            "description": "Single business review analysis with AI-powered insights"
        },
        "pro": {
            "name": "Pro",
            "price": 79.99,
            "description": "Up to 5 business analyses with advanced AI insights"
        },
        "enterprise": {
            "name": "Enterprise",
            "price": 199.99,
            "description": "Unlimited business analyses with premium AI insights"
        }
    }
    
    plan_info = plans.get(plan, plans["basic"])
    
    return templates.TemplateResponse(
        "checkout.html",
        {
            "request": request,
            "user": user,
            "plan": plan,
            "plan_info": plan_info,
            "stripe_publishable_key": STRIPE_PUBLISHABLE_KEY
        }
    )

@app.post("/api/create-payment-intent")
async def create_payment_intent(request: Request, db: Session = Depends(get_db)):
    try:
        from app.stripe_config import stripe_api
        
        data = await request.json()
        amount = int(float(data.get("amount", 0)) * 100)  # Convert to cents
        
        intent = stripe_api.create_payment_intent(
            amount=amount,
            currency="usd",
            description=data.get("description", "AI Review Analyzer")
        )
        
        return {"client_secret": intent.client_secret}
    except Exception as e:
        print(f"Error creating payment intent: {str(e)}")
        return {"error": str(e)}, 400

@app.post("/api/confirm-payment")
async def confirm_payment(request: Request, db: Session = Depends(get_db)):
    try:
        from app.stripe_config import stripe_api
        
        data = await request.json()
        payment_intent_id = data.get("payment_intent_id")
        
        # Verify payment with Stripe
        intent = stripe_api.retrieve_payment_intent(payment_intent_id)
        
        if intent.status != "succeeded":
            return {"error": "Payment not completed"}, 400
        
        # Get current user
        token = request.cookies.get("access_token")
        if not token:
            return {"error": "Not authenticated"}, 401
        
        payload = decode_token(token)
        if not payload:
            return {"error": "Invalid token"}, 401
        
        email = payload.get("sub")
        user = get_user_by_email(db, email)
        if not user:
            return {"error": "User not found"}, 404
        
        # Create payment record
        try:
            db.execute(
                text('INSERT INTO "Payment" ("userId", stripe_payment_intent_id, stripe_charge_id, amount, currency, status, "createdAt", "updatedAt") VALUES (:userId, :stripe_payment_intent_id, :stripe_charge_id, :amount, :currency, :status, :createdAt, :updatedAt)'),
                {
                    "userId": user.id,
                    "stripe_payment_intent_id": payment_intent_id,
                    "stripe_charge_id": intent.charges.data[0].id if intent.charges.data else None,
                    "amount": intent.amount / 100,
                    "currency": intent.currency,
                    "status": "succeeded",
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }
            )
            db.commit()
        except Exception as e:
            print(f"Error creating payment record: {str(e)}")
            db.rollback()
        
        return {"success": True}
    except Exception as e:
        print(f"Error confirming payment: {str(e)}")
        return {"error": str(e)}, 400

@app.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        from app.stripe_config import stripe_api
        
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        event = stripe_api.verify_webhook(payload, sig_header)
        
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            print(f"Payment succeeded: {payment_intent['id']}")
        elif event["type"] == "payment_intent.payment_failed":
            payment_intent = event["data"]["object"]
            print(f"Payment failed: {payment_intent['id']}")
        
        return {"status": "success"}
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return {"error": str(e)}, 400

@app.get("/payment-success", response_class=HTMLResponse)
async def payment_success(request: Request):
    user = None
    try:
        token = request.cookies.get("access_token")
        if token:
            payload = decode_token(token)
            if payload:
                email = payload.get("sub")
                if email:
                    db = next(get_db())
                    try:
                        user = get_user_by_email(db, email)
                    finally:
                        db.close()
    except:
        pass
    
    return templates.TemplateResponse("payment-success.html", {"request": request, "user": user})

@app.get("/payment-failed", response_class=HTMLResponse)
async def payment_failed(request: Request):
    user = None
    try:
        token = request.cookies.get("access_token")
        if token:
            payload = decode_token(token)
            if payload:
                email = payload.get("sub")
                if email:
                    db = next(get_db())
                    try:
                        user = get_user_by_email(db, email)
                    finally:
                        db.close()
    except:
        pass
    
    return templates.TemplateResponse("payment-failed.html", {"request": request, "user": user})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
