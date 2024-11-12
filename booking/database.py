from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./hotel_booking.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={
        "check_same_thread": False, 
        "timeout": 30, 
        "isolation_level": "IMMEDIATE"
    }
)

engine.connect().execute(text("PRAGMA foreign_keys=ON"))  # توجه کنید که foreign_keys باید درست نوشته شود
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ایجاد Base برای تعریف مدل‌ها
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


