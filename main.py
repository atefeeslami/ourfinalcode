from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from routers import users, hotels, bookings, notifications, reviews, discounts, wallets, support_tickets, wishlist
from routers import auth_router  # این مسیر را مطابق با پوشه‌ای که روتر در آن است تنظیم کنید

# تعریف مسیر برای توکن
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

# ایجاد اپلیکیشن FastAPI
app = FastAPI()

@app.on_event("startup")
def configure_openapi():
    # این تابع برای اضافه کردن اطلاعات امنیتی به OpenAPI در زمان راه‌اندازی استفاده می‌شود
    if app.openapi_schema:
        app.openapi_schema['components'] = {
            'securitySchemes': {
                "OAuth2PasswordBearer": {
                    "type": "oauth2",
                    "flows": {
                        "password": {
                            "tokenUrl": "/users/token"
                        }
                    }
                }
            }
        }

# اضافه کردن روت‌ها
app.include_router(users.router)
app.include_router(hotels.router)
app.include_router(bookings.router)
app.include_router(notifications.router)
app.include_router(reviews.router)
app.include_router(discounts.router)
app.include_router(wallets.router)
app.include_router(support_tickets.router)
app.include_router(wishlist.router)
app.include_router(auth_router.router)