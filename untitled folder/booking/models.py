from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from booking.database import Base




# پایه SQLAlchemy برای تعریف مدل‌ها


# مدل User


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    phone_number = Column(String)
    
    # رابطه با هتل‌ها
    hotels = relationship("Hotel", back_populates="manager")
    bookings = relationship("Booking", back_populates="user")

class Hotel(Base):
    __tablename__ = 'hotels'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    description = Column(String)
    has_wifi = Column(Boolean, default=True)
    price_per_night = Column(Float)
    
    # ارتباط با کاربر (مدیر هتل)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    manager = relationship("User", back_populates="hotels")
    # ارتباط با Booking
    bookings = relationship("Booking", back_populates="hotel")

# مدل Booking
class Booking(Base):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    hotel_id = Column(Integer, ForeignKey('hotels.id'))
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    status = Column(String, default="Pending")
    user = relationship("User", back_populates="bookings")
    hotel = relationship("Hotel", back_populates="bookings")
