import random
from datetime import datetime, timezone

import numpy as np
from sqlalchemy.orm import Session

from models import MarketData, Trade, TradeCreate


def _now():
    return datetime.now(timezone.utc)


class TradeService:
    @staticmethod
    def create_trade(db: Session, trade: TradeCreate, buyer_id: int) -> Trade:
        db_trade = Trade(
            buyer_id=buyer_id,
            seller_id=trade.seller_id,
            energy_type=trade.energy_type,
            quantity=trade.quantity,
            price=trade.price,
            total=round(trade.quantity * trade.price, 4),
            status="open",
        )
        db.add(db_trade)
        db.commit()
        db.refresh(db_trade)
        return db_trade

    @staticmethod
    def list_trades(db: Session, user_id: int, skip: int = 0, limit: int = 20):
        return (
            db.query(Trade)
            .filter((Trade.buyer_id == user_id) | (Trade.seller_id == user_id))
            .order_by(Trade.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def all_trades(db: Session, skip: int = 0, limit: int = 50):
        return db.query(Trade).order_by(Trade.created_at.desc()).offset(skip).limit(limit).all()


class MarketSimulator:
    ENERGY_TYPES = ["solar", "wind", "hydro", "biomass"]
    BASE_PRICES = {"solar": 38.0, "wind": 42.0, "hydro": 55.0, "biomass": 70.0}

    @classmethod
    def generate_snapshot(cls) -> dict:
        hour = datetime.now(timezone.utc).hour
        solar = max(0.0, 500 * np.sin(np.pi * hour / 12) + random.gauss(0, 30))
        wind = max(0.0, 300 + random.gauss(0, 80))
        demand = 600 + 200 * np.cos(np.pi * (hour - 18) / 12) + random.gauss(0, 40)
        renewable_surplus = solar + wind - demand
        spot_price = max(10.0, 80.0 - 0.05 * renewable_surplus + random.gauss(0, 5))
        carbon_intensity = max(0.0, 300 - 0.3 * (solar + wind) + random.gauss(0, 20))
        return {
            "solar_generation": float(round(solar, 2)),
            "wind_generation": float(round(wind, 2)),
            "demand": float(round(demand, 2)),
            "spot_price": float(round(spot_price, 2)),
            "carbon_intensity": float(round(carbon_intensity, 2)),
        }

    @classmethod
    def persist_snapshot(cls, db: Session) -> MarketData:
        snap = cls.generate_snapshot()
        record = MarketData(**snap)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @classmethod
    def optimize_routing(cls, energy_type: str, quantity: float) -> dict:
        base = cls.BASE_PRICES.get(energy_type, 60.0)
        noise = random.gauss(0, base * 0.05)
        recommended_price = round(max(5.0, base + noise), 2)
        confidence = round(random.uniform(0.70, 0.98), 3)
        return {
            "energy_type": energy_type,
            "quantity_mwh": quantity,
            "recommended_price": recommended_price,
            "estimated_total": round(recommended_price * quantity, 2),
            "confidence": confidence,
            "routing_strategy": "merit_order_optimization",
        }


trade_service = TradeService()
market_simulator = MarketSimulator()
