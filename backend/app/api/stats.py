from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.bot import Bot
from app.models.order import Order
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bots_count = db.query(func.count(Bot.id)).filter(Bot.user_id == current_user.id).scalar()
    active_bots = db.query(func.count(Bot.id)).filter(
        Bot.user_id == current_user.id,
        Bot.status == "active"
    ).scalar()
    
    orders_count = db.query(func.count(Order.id)).join(Bot).filter(
        Bot.user_id == current_user.id
    ).scalar()
    
    filled_orders = db.query(func.count(Order.id)).join(Bot).filter(
        Bot.user_id == current_user.id,
        Order.status == "filled"
    ).scalar()
    
    return {
        "bots_total": bots_count or 0,
        "bots_active": active_bots or 0,
        "orders_total": orders_count or 0,
        "orders_filled": filled_orders or 0
    }

@router.get("/history")
async def get_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    orders = db.query(Order).join(Bot).filter(
        Bot.user_id == current_user.id
    ).order_by(Order.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": order.id,
            "bot_id": order.bot_id,
            "symbol": order.symbol,
            "side": order.side.value,
            "status": order.status.value,
            "quantity": float(order.quantity),
            "price": float(order.price) if order.price else None,
            "created_at": order.created_at.isoformat()
        }
        for order in orders
    ]
