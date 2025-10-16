from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "User"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Text, primary_key=True, index=True)
    name = Column(Text, nullable=True)
    email = Column(Text, unique=True, index=True, nullable=False)
    password = Column(Text, nullable=False)
    emailVerified = Column(DateTime, nullable=True)
    image = Column(Text, nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    orders = relationship("Order", back_populates="user", foreign_keys="Order.userId")
    payments = relationship("Payment", back_populates="user", foreign_keys="Payment.userId")
    accounts = relationship("Account", back_populates="user", foreign_keys="Account.userId")
    sessions = relationship("Session", back_populates="user", foreign_keys="Session.userId")

class Order(Base):
    __tablename__ = "Order"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Text, primary_key=True, index=True)
    userId = Column(Text, ForeignKey("User.id"), nullable=False)
    business_name = Column(String, nullable=False)
    business_address = Column(String, nullable=False)
    status = Column(String, default="pending")
    price = Column(Float, default=29.99)
    payment_id = Column(Integer, ForeignKey("Payment.id"), nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="orders", foreign_keys=[userId])
    payment = relationship("Payment", back_populates="order")

class Payment(Base):
    __tablename__ = "Payment"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Text, ForeignKey("User.id"), nullable=False)
    stripe_payment_intent_id = Column(String, unique=True, nullable=False)
    stripe_charge_id = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="usd")
    status = Column(String, default="pending")
    description = Column(String, nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="payments", foreign_keys=[userId])
    order = relationship("Order", back_populates="payment")

class Account(Base):
    __tablename__ = "Account"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Text, primary_key=True, index=True)
    userId = Column(Text, ForeignKey("User.id"), nullable=False)
    type = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    providerAccountId = Column(String, nullable=False)
    refresh_token = Column(Text, nullable=True)
    access_token = Column(Text, nullable=True)
    expires_at = Column(Integer, nullable=True)
    token_type = Column(String, nullable=True)
    scope = Column(String, nullable=True)
    id_token = Column(Text, nullable=True)
    session_state = Column(String, nullable=True)
    
    user = relationship("User", back_populates="accounts", foreign_keys=[userId])

class Session(Base):
    __tablename__ = "Session"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Text, primary_key=True, index=True)
    sessionToken = Column(String, unique=True, nullable=False)
    userId = Column(Text, ForeignKey("User.id"), nullable=False)
    expires = Column(DateTime, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="sessions", foreign_keys=[userId])

class VerificationToken(Base):
    __tablename__ = "VerificationToken"
    __table_args__ = {'extend_existing': True}
    
    identifier = Column(String, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False)
    expires = Column(DateTime, nullable=False)
