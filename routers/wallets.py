from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from booking.database import get_db
from booking.models import Wallet, User
from booking.auth import get_current_user
from pydantic import BaseModel
from typing import Optional
from datetime import datetime  # اضافه کردن این خط

router = APIRouter(
    prefix="/wallet",
    tags=["wallet"]
)

class WalletResponse(BaseModel):
    balance: float
    points: int
    last_updated: datetime

# API برای مشاهده کیف پول کاربر
@router.get("/", response_model=WalletResponse)
def get_wallet(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet

# API برای افزایش اعتبار
class AddFundsRequest(BaseModel):
    amount: float

@router.post("/add_funds")
def add_funds(request: AddFundsRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet:
        wallet = Wallet(user_id=current_user.id, balance=request.amount)
        db.add(wallet)
    else:
        wallet.balance += request.amount
    wallet.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(wallet)
    return {"message": "Funds added successfully", "balance": wallet.balance}

# API برای استفاده از امتیازها
class RedeemPointsRequest(BaseModel):
    points: int

@router.post("/redeem_points")
def redeem_points(request: RedeemPointsRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet or wallet.points < request.points:
        raise HTTPException(status_code=400, detail="Insufficient points")
    wallet.points -= request.points
    wallet.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(wallet)
    return {"message": "Points redeemed successfully", "remaining_points": wallet.points}