from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from app.models.order import OrderStatus, OrderSide, OrderType
from typing import Optional

class OrderCreate(BaseModel):
    bot_id: int
    symbol: str
    side: OrderSide
    type: OrderType
    quantity: Decimal
    price: Optional[Decimal] = None

class OrderResponse(BaseModel):
    id: int
    bot_id: int
    exchange_order_id: Optional[str] = None
    symbol: str
    side: OrderSide
    type: OrderType
    status: OrderStatus
    price: Optional[Decimal] = None
    quantity: Decimal
    filled_quantity: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
