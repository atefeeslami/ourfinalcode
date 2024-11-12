
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from booking.database import Base
from datetime import datetime

# مدل User
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    phone_number = Column(String)
    role = Column(String, default="user")  # user, admin, hotel_manager
    points = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hotels = relationship("Hotel", back_populates="manager")
    bookings = relationship("Booking", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    support_tickets = relationship("SupportTicket", back_populates="user")
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    wishlist = relationship("Wishlist", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

# مدل Hotel
class Hotel(Base):
    __tablename__ = 'hotels'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    description = Column(String)
    has_wifi = Column(Boolean, default=True)
    price_per_night = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    manager = relationship("User", back_populates="hotels")
    bookings = relationship("Booking", back_populates="hotel")
    reviews = relationship("Review", back_populates="hotel")
    wishlist_entries = relationship("Wishlist", back_populates="hotel")

# مدل Booking
class Booking(Base):
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    hotel_id = Column(Integer, ForeignKey('hotels.id'))
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    status = Column(String, default="Pending")  # Pending, Confirmed, Cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="bookings")
    hotel = relationship("Hotel", back_populates="bookings")
    discounts = relationship("BookingDiscount", back_populates="booking")

# مدل Review
class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    hotel_id = Column(Integer, ForeignKey('hotels.id'))
    rating = Column(Integer, nullable=False)
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="reviews")
    hotel = relationship("Hotel", back_populates="reviews")

# مدل SupportTicket
class SupportTicket(Base):
    __tablename__ = 'support_tickets'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject = Column(String, nullable=False)
    description = Column(String)
    status = Column(String, default="Open")  # Open, Closed, In Progress
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="support_tickets")

# مدل Wallet
class Wallet(Base):
    __tablename__ = 'wallet'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    balance = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="wallet")

# مدل Wishlist
class Wishlist(Base):
    __tablename__ = 'wishlist'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    hotel_id = Column(Integer, ForeignKey('hotels.id'), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="wishlist")
    hotel = relationship("Hotel", back_populates="wishlist_entries")

# مدل Discount
class Discount(Base):
    __tablename__ = 'discounts'
    



    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    description = Column(String)
    discount_percentage = Column(Float, nullable=False)
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BookingDiscount(Base):
    __tablename__ = 'booking_discounts'
    
    booking_id = Column(Integer, ForeignKey('bookings.id'), primary_key=True)
    discount_id = Column(Integer, ForeignKey('discounts.id'), primary_key=True)

    booking = relationship("Booking", back_populates="discounts")
    discount = relationship("Discount")

# مدل Notification
class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    booking_id = Column(Integer, ForeignKey('bookings.id'), nullable=True)
    type = Column(String)  # Booking, Payment, Reminder, etc.
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_status = Column(Boolean, default=False)

    user = relationship("User", back_populates="notifications")
    booking = relationship("Booking", back_populates="notifications", uselist=False)

