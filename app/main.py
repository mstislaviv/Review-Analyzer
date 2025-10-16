from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Order
from app.auth import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    get_current_user_from_cookie,
    require_auth
)

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
            from app.auth import decode_token
            payload = decode_token(token)
            if payload:
                email = payload.get("sub")
                if email:
                    db = next(get_db())
                    try:
                        user = db.query(User).filter(User.email == email).first()
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
            from app.auth import decode_token
            payload = decode_token(token)
            if payload:
                email = payload.get("sub")
                if email:
                    db = next(get_db())
                    try:
                        user = db.query(User).filter(User.email == email).first()
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
        user = db.query(User).filter(User.email == email).first()
        
        if not user or not verify_password(password, user.password):
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Invalid email or password", "user": None}
            )
        
        token = create_access_token({"sub": user.email})
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="access_token", value=token, httponly=True)
        return response
    except Exception as e:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": f"Login error: {str(e)}", "user": None}
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
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error": "User already exists with this email", "user": None}
            )
        
        hashed_password = get_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        token = create_access_token({"sub": new_user.email})
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="access_token", value=token, httponly=True)
        return response
    except Exception as e:
        db.rollback()
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": f"Signup error: {str(e)}", "user": None}
        )

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth)
):
    try:
        orders = db.query(Order).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).all()
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "user": user, "orders": orders}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "user": user, "orders": [], "error": f"Error loading orders: {str(e)}"}
        )

@app.post("/dashboard")
async def create_order(
    request: Request,
    business_name: str = Form(...),
    business_address: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_auth)
):
    try:
        new_order = Order(
            user_id=user.id,
            business_name=business_name,
            business_address=business_address,
            status="pending"
        )
        db.add(new_order)
        db.commit()
        
        orders = db.query(Order).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).all()
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user,
                "orders": orders,
                "message": "Order submitted successfully! We'll analyze your reviews and send you a report."
            }
        )
    except Exception as e:
        db.rollback()
        orders = db.query(Order).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).all()
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "user": user, "orders": orders, "error": f"Error creating order: {str(e)}"}
        )

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="access_token")
    return response

@app.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request):
    user = None
    try:
        token = request.cookies.get("access_token")
        if token:
            from app.auth import decode_token
            payload = decode_token(token)
            if payload:
                email = payload.get("sub")
                if email:
                    db = next(get_db())
                    try:
                        user = db.query(User).filter(User.email == email).first()
                    finally:
                        db.close()
    except:
        pass
    
    return templates.TemplateResponse("privacy.html", {"request": request, "user": user})

@app.get("/terms", response_class=HTMLResponse)
async def terms(request: Request):
    user = None
    try:
        token = request.cookies.get("access_token")
        if token:
            from app.auth import decode_token
            payload = decode_token(token)
            if payload:
                email = payload.get("sub")
                if email:
                    db = next(get_db())
                    try:
                        user = db.query(User).filter(User.email == email).first()
                    finally:
                        db.close()
    except:
        pass
    
    return templates.TemplateResponse("terms.html", {"request": request, "user": user})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
