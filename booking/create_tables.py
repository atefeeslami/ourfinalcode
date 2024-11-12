from booking.database import Base, engine
from booking import models

# ایجاد جداول در دیتابیس
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()

