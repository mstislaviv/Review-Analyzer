from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
import os
import warnings

# Suppress bcrypt version warning
warnings.filterwarnings("ignore", category=DeprecationWarning)

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
MAX_PASSWORD_LENGTH = 72  # bcrypt limit

# Create password context with error handling
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception as e:
    print(f"Warning: CryptContext initialization issue: {str(e)}")
    # Fallback to basic bcrypt
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer(auto_error=False)

def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password and return (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    
    return True, ""

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    try:
        # Truncate password to bcrypt limit before verification
        plain_password = plain_password[:MAX_PASSWORD_LENGTH]
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Password verification error: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    """Hash a password, truncating to bcrypt limit"""
    try:
        # Truncate password to bcrypt limit before hashing
        password = password[:MAX_PASSWORD_LENGTH]
        return pwd_context.hash(password)
    except Exception as e:
        print(f"Password hashing error: {str(e)}")
        raise ValueError(f"Error hashing password: {str(e)}")

def create_access_token(data: dict):
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    """Decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    """Get current user from authentication cookie"""
    try:
        token = request.cookies.get("access_token")
        if not token:
            return None
        
        payload = decode_token(token)
        if payload is None:
            return None
        
        email = payload.get("sub")
        if email is None:
            return None
        
        user = db.query(User).filter(User.email == email).first()
        return user
    except Exception:
        return None

def require_auth(request: Request, db: Session = Depends(get_db)):
    """Require authentication for protected routes"""
    try:
        user = get_current_user_from_cookie(request, db)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication error"
        )
