from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


def _now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=_now)
    trades_bought = relationship("Trade", foreign_keys="[Trade.buyer_id]", back_populates="buyer")
    trades_sold = relationship("Trade", foreign_keys="[Trade.seller_id]", back_populates="seller")


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    energy_type = Column(String(50), index=True, nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(String(20), default="open")
    created_at = Column(DateTime(timezone=True), default=_now, index=True)
    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="trades_bought")
    seller = relationship("User", foreign_keys=[seller_id], back_populates="trades_sold")


class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), default=_now, index=True)
    solar_generation = Column(Float, nullable=False)
    wind_generation = Column(Float, nullable=False)
    demand = Column(Float, nullable=False)
    spot_price = Column(Float, nullable=False)
    carbon_intensity = Column(Float, nullable=True)


class TradeCreate(BaseModel):
    energy_type: str
    quantity: float
    price: float
    seller_id: Optional[int] = None


class TradeOut(BaseModel):
    id: int
    buyer_id: int
    seller_id: Optional[int]
    energy_type: str
    quantity: float
    price: float
    total: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MarketDataOut(BaseModel):
    id: int
    timestamp: datetime
    solar_generation: float
    wind_generation: float
    demand: float
    spot_price: float
    carbon_intensity: Optional[float]

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
