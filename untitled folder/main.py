from fastapi import FastAPI
from routers import users, hotels, bookings  # فقط فایل‌های موجود

app = FastAPI()

app.include_router(users.router)
app.include_router(hotels.router)
app.include_router(bookings.router)