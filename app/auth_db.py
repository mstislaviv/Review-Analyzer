"""
Database functions for authentication using raw SQL to avoid SQLAlchemy quoting issues
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.auth import get_password_hash, verify_password
from datetime import datetime
import uuid

class User:
    """Simple User class to hold user data"""
    def __init__(self, id, name, email, password, emailVerified=None, image=None, createdAt=None, updatedAt=None):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.emailVerified = emailVerified
        self.image = image
        self.createdAt = createdAt
        self.updatedAt = updatedAt

def get_user_by_email(db: Session, email: str) -> User:
    """Get user by email using raw SQL"""
    try:
        result = db.execute(
            text('SELECT id, name, email, password, "emailVerified", image, "createdAt", "updatedAt" FROM "User" WHERE email = :email'),
            {"email": email.lower()}
        )
        row = result.fetchone()
        if row:
            return User(
                id=row[0],
                name=row[1],
                email=row[2],
                password=row[3],
                emailVerified=row[4],
                image=row[5],
                createdAt=row[6],
                updatedAt=row[7]
            )
        return None
    except Exception as e:
        print(f"Error getting user by email: {str(e)}")
        # Reset transaction on error
        try:
            db.rollback()
        except:
            pass
        return None

def get_user_by_id(db: Session, user_id: str) -> User:
    """Get user by ID using raw SQL"""
    try:
        result = db.execute(
            text('SELECT id, name, email, password, "emailVerified", image, "createdAt", "updatedAt" FROM "User" WHERE id = :id'),
            {"id": user_id}
        )
        row = result.fetchone()
        if row:
            return User(
                id=row[0],
                name=row[1],
                email=row[2],
                password=row[3],
                emailVerified=row[4],
                image=row[5],
                createdAt=row[6],
                updatedAt=row[7]
            )
        return None
    except Exception as e:
        print(f"Error getting user by ID: {str(e)}")
        # Reset transaction on error
        try:
            db.rollback()
        except:
            pass
        return None

def create_user(db: Session, name: str, email: str, password: str) -> User:
    """Create a new user using raw SQL"""
    try:
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(password)
        now = datetime.utcnow()
        
        db.execute(
            text('INSERT INTO "User" (id, name, email, password, "createdAt", "updatedAt") VALUES (:id, :name, :email, :password, :createdAt, :updatedAt)'),
            {
                "id": user_id,
                "name": name,
                "email": email.lower(),
                "password": hashed_password,
                "createdAt": now,
                "updatedAt": now
            }
        )
        db.commit()
        
        return User(
            id=user_id,
            name=name,
            email=email.lower(),
            password=hashed_password,
            createdAt=now,
            updatedAt=now
        )
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        try:
            db.rollback()
        except:
            pass
        raise

def user_exists(db: Session, email: str) -> bool:
    """Check if user exists using raw SQL"""
    try:
        result = db.execute(
            text('SELECT id FROM "User" WHERE email = :email'),
            {"email": email.lower()}
        )
        return result.fetchone() is not None
    except Exception as e:
        print(f"Error checking if user exists: {str(e)}")
        # Reset transaction on error
        try:
            db.rollback()
        except:
            pass
        return False

def get_user_orders(db: Session, user_id: str):
    """Get user's orders using raw SQL"""
    try:
        result = db.execute(
            text('SELECT id, "userId", business_name, business_address, status, price, "createdAt", "updatedAt" FROM "Order" WHERE "userId" = :userId ORDER BY "createdAt" DESC'),
            {"userId": user_id}
        )
        rows = result.fetchall()
        orders = []
        for row in rows:
            orders.append({
                'id': row[0],
                'userId': row[1],
                'business_name': row[2],
                'business_address': row[3],
                'status': row[4],
                'price': row[5],
                'createdAt': row[6],
                'updatedAt': row[7]
            })
        return orders
    except Exception as e:
        print(f"Error getting user orders: {str(e)}")
        # Reset transaction on error
        try:
            db.rollback()
        except:
            pass
        return []
