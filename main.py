import os
from contextlib import asynccontextmanager
from datetime import timedelta

import httpx
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import create_access_token, get_current_user, hash_password, verify_password
from database import SessionLocal, get_db, init_db
from models import MarketData, MarketDataOut, TokenResponse, TradeCreate, TradeOut, User
from services import market_simulator, trade_service


DAO_HUB_URL = os.getenv("DAO_HUB_URL", "http://localhost:8000/api/v1")


async def push_to_dao(key: str, value: float, unit: str = "") -> None:
    node_id = os.getenv("DAO_NODE_ID", "")
    if not node_id:
        return
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            await client.post(
                f"{DAO_HUB_URL}/ecosystem/nodes/{node_id}/metrics",
                json={"key": key, "value": value, "unit": unit},
            )
    except Exception:
        pass


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        if not db.query(User).filter_by(email="admin@energy.local").first():
            db.add(User(email="admin@energy.local", hashed_password=hash_password(os.getenv("ADMIN_PASSWORD", "changeme"))))
            db.commit()
    finally:
        db.close()
    yield


app = FastAPI(
    title="DAO Renewable Energy Trading",
    description="Synthetic renewable market data, trading workflows, and optimization for the Sampo AI OS ecosystem.",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

API = "/api/v1"


@app.get("/")
async def root():
    return {"service": "dao-renewable-energy-trading", "role": "Renewable energy trading node", "docs": "/docs"}


@app.post(f"{API}/auth/token", response_model=TokenResponse, tags=["auth"])
async def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=form.username, is_active=True).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.email}, timedelta(hours=8))
    return {"access_token": token}


@app.get(f"{API}/market/latest", response_model=MarketDataOut, tags=["market"])
async def get_latest_market(db: Session = Depends(get_db)):
    record = market_simulator.persist_snapshot(db)
    await push_to_dao("spot_price", record.spot_price, "EUR/MWh")
    await push_to_dao("solar_generation", record.solar_generation, "MW")
    await push_to_dao("wind_generation", record.wind_generation, "MW")
    await push_to_dao("carbon_intensity", record.carbon_intensity or 0.0, "gCO2/kWh")
    return record


@app.get(f"{API}/market/history", response_model=list[MarketDataOut], tags=["market"])
async def get_market_history(limit: int = 24, db: Session = Depends(get_db)):
    rows = db.query(MarketData).order_by(MarketData.timestamp.desc()).limit(limit).all()
    return rows


@app.post(f"{API}/trades", response_model=TradeOut, status_code=201, tags=["trades"])
async def create_trade(body: TradeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    trade = trade_service.create_trade(db, body, current_user.id)
    await push_to_dao("trade_volume_mwh", trade.quantity, "MWh")
    await push_to_dao("trade_value_eur", trade.total, "EUR")
    return trade


@app.get(f"{API}/trades", response_model=list[TradeOut], tags=["trades"])
async def list_my_trades(skip: int = 0, limit: int = 20, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return trade_service.list_trades(db, current_user.id, skip, limit)


@app.get(f"{API}/trades/all", response_model=list[TradeOut], tags=["trades"])
async def list_all_trades(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return trade_service.all_trades(db, skip, limit)


@app.post(f"{API}/optimize", tags=["ai"])
async def optimize_routing(energy_type: str = "solar", quantity: float = 100.0):
    return market_simulator.optimize_routing(energy_type, quantity)


@app.get("/health", tags=["system"])
async def health(db: Session = Depends(get_db)):
    return {
        "status": "ok",
        "service": "dao-renewable-energy-trading",
        "version": "1.0.0",
        "active_users": db.query(User).filter(User.is_active == True).count(),
        "market_snapshots": db.query(MarketData).count(),
    }
