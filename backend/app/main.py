from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api import auth, bots, orders, notifications, stats
from app.core.logging_config import setup_logging

setup_logging()

app = FastAPI(
    title="Trading Bot API",
    description="API для управления торговыми ботами Binance и Bybit",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Trading Bot API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(bots.router, prefix="/api/bots", tags=["bots"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
