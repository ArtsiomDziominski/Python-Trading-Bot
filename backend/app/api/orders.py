from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import OrderService
from app.core.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = OrderService(db)
    order = service.create_order(order_data, current_user.id)
    return order

@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    bot_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = OrderService(db)
    orders = service.get_user_orders(current_user.id, bot_id)
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = OrderService(db)
    order = service.get_order(order_id, current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
