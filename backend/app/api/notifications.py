from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.notification import NotificationSettingsCreate, NotificationSettingsResponse, NotificationSettingsUpdate
from app.services.notification_service import NotificationService
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/settings", response_model=NotificationSettingsResponse)
async def get_notification_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    settings = service.get_user_settings(current_user.id)
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings

@router.post("/settings", response_model=NotificationSettingsResponse, status_code=status.HTTP_201_CREATED)
async def create_notification_settings(
    settings_data: NotificationSettingsCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    settings = service.create_settings(settings_data, current_user.id)
    return settings

@router.put("/settings", response_model=NotificationSettingsResponse)
async def update_notification_settings(
    settings_data: NotificationSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    settings = service.update_settings(settings_data, current_user.id)
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings
