from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.bot import Bot
from app.schemas.bot import BotCreate, BotUpdate, BotResponse
from app.services.bot_service import BotService
from app.core.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=BotResponse, status_code=status.HTTP_201_CREATED)
async def create_bot(
    bot_data: BotCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = BotService(db)
    bot = service.create_bot(bot_data, current_user.id)
    return bot

@router.get("/", response_model=List[BotResponse])
async def get_bots(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = BotService(db)
    bots = service.get_user_bots(current_user.id)
    return bots

@router.get("/{bot_id}", response_model=BotResponse)
async def get_bot(
    bot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = BotService(db)
    bot = service.get_bot(bot_id, current_user.id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot

@router.put("/{bot_id}", response_model=BotResponse)
async def update_bot(
    bot_id: int,
    bot_data: BotUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = BotService(db)
    bot = service.update_bot(bot_id, bot_data, current_user.id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot

@router.delete("/{bot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bot(
    bot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = BotService(db)
    success = service.delete_bot(bot_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Bot not found")
