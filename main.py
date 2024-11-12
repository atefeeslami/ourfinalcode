from fastapi import FastAPI
from routers import users, hotels, bookings, notifications, reviews, discounts, wallets, support_tickets,wishlist # سایر فایل‌های موجود
app = FastAPI()

app.include_router(users.router)
app.include_router(hotels.router)
app.include_router(bookings.router)
app.include_router(notifications.router)
app.include_router(reviews.router)
app.include_router(discounts.router)
app.include_router(wallets.router)
app.include_router(support_tickets.router)
app.include_router(wishlist.router)




