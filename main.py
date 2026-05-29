import os
import random
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, relationship, sessionmaker

DATABASE_URL = "sqlite:///./nba_market.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

app = FastAPI(title="NBA Playoffs Prediction Market")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Market(Base):
    __tablename__ = "markets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    team_a = Column(String(128), nullable=False)
    team_b = Column(String(128), nullable=False)
    odds_a = Column(Float, default=50.0)
    odds_b = Column(Float, default=50.0)
    volume = Column(Float, default=0.0)
    prediction_count = Column(Integer, default=0)
    status = Column(String(32), default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    predictions = relationship("Prediction", back_populates="market")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(128), unique=True, nullable=False, index=True)
    points = Column(Float, default=0.0)
    predictions_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    predictions = relationship("Prediction", back_populates="user")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False)
    predicted_winner = Column(String(128), nullable=False)
    amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    market = relationship("Market", back_populates="predictions")
    user = relationship("User", back_populates="predictions")


class PredictionCreate(BaseModel):
    user_id: int
    market_id: int
    predicted_winner: str
    amount: float


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    existing = db.query(Market).first()
    if existing:
        db.close()
        return

    now = datetime.utcnow()

    conferences = [
        {
            "title": "Eastern Conference First Round",
            "series": [
                ("Cleveland Cavaliers", "Boston Celtics"),
                ("New York Knicks", "Philadelphia 76ers"),
                ("Milwaukee Bucks", "Indiana Pacers"),
                ("Miami Heat", "Orlando Magic"),
            ],
        },
        {
            "title": "Western Conference First Round",
            "series": [
                ("Oklahoma City Thunder", "Denver Nuggets"),
                ("Minnesota Timberwolves", "Dallas Mavericks"),
                ("Los Angeles Lakers", "Golden State Warriors"),
                ("Phoenix Suns", "Memphis Grizzlies"),
            ],
        },
    ]

    markets = []
    for conf in conferences:
        for team_a, team_b in conf["series"]:
            odds_a = round(random.uniform(35, 65), 1)
            odds_b = round(100 - odds_a, 1)
            volume = round(random.uniform(10000, 150000), 2)
            pred_count = random.randint(50, 500)
            market = Market(
                title=f"{team_a} vs {team_b}",
                team_a=team_a,
                team_b=team_b,
                odds_a=odds_a,
                odds_b=odds_b,
                volume=volume,
                prediction_count=pred_count,
                status="open",
                created_at=now,
                updated_at=now,
            )
            markets.append(market)

    db.add_all(markets)
    db.commit()

    usernames = [
        "hoop_guru", "bracket_buster", "rim_rocket", "swish_king",
        "pivot_master", "three_eye", "dime_dropper", "clutch_bandit",
    ]
    users = []
    for name in usernames:
        pts = round(random.uniform(500, 5000), 1)
        user = User(username=name, points=pts, predictions_count=random.randint(5, 80))
        users.append(user)
    db.add_all(users)
    db.commit()

    for market in markets:
        for user in random.sample(users, random.randint(3, 6)):
            winner = random.choice([market.team_a, market.team_b])
            amt = round(random.uniform(10, 500), 2)
            pred = Prediction(
                user_id=user.id,
                market_id=market.id,
                predicted_winner=winner,
                amount=amt,
            )
            db.add(pred)
    db.commit()
    db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/markets")
def list_markets():
    db = next(get_db())
    markets = db.query(Market).all()
    result = []
    for m in markets:
        result.append({
            "id": m.id,
            "title": m.title,
            "team_a": m.team_a,
            "team_b": m.team_b,
            "odds_a": m.odds_a,
            "odds_b": m.odds_b,
            "volume": m.volume,
            "prediction_count": m.prediction_count,
            "status": m.status,
        })
    db.close()
    return {"markets": result}


@app.get("/api/market/{market_id}")
def get_market(market_id: int):
    db = next(get_db())
    m = db.query(Market).filter(Market.id == market_id).first()
    if not m:
        db.close()
        return JSONResponse(status_code=404, content={"error": "Market not found"})
    preds = db.query(Prediction).filter(Prediction.market_id == market_id).all()
    result = {
        "id": m.id,
        "title": m.title,
        "team_a": m.team_a,
        "team_b": m.team_b,
        "odds_a": m.odds_a,
        "odds_b": m.odds_b,
        "volume": m.volume,
        "prediction_count": m.prediction_count,
        "status": m.status,
        "predictions": [
            {
                "id": p.id,
                "user_id": p.user_id,
                "predicted_winner": p.predicted_winner,
                "amount": p.amount,
                "created_at": p.created_at.isoformat(),
            }
            for p in preds
        ],
    }
    db.close()
    return result


@app.post("/api/predictions")
def create_prediction(body: PredictionCreate):
    db = next(get_db())
    market = db.query(Market).filter(Market.id == body.market_id).first()
    if not market:
        db.close()
        return JSONResponse(status_code=404, content={"error": "Market not found"})
    user = db.query(User).filter(User.id == body.user_id).first()
    if not user:
        db.close()
        return JSONResponse(status_code=404, content={"error": "User not found"})
    if body.predicted_winner not in (market.team_a, market.team_b):
        db.close()
        return JSONResponse(status_code=400, content={"error": "Invalid predicted winner"})

    pred = Prediction(
        user_id=body.user_id,
        market_id=body.market_id,
        predicted_winner=body.predicted_winner,
        amount=body.amount,
    )
    db.add(pred)

    market.prediction_count += 1
    market.volume += body.amount

    total_a = (
        db.query(Prediction)
        .filter(Prediction.market_id == body.market_id, Prediction.predicted_winner == market.team_a)
        .count()
        + (1 if body.predicted_winner == market.team_a else 0)
    )
    total_b = (
        db.query(Prediction)
        .filter(Prediction.market_id == body.market_id, Prediction.predicted_winner == market.team_b)
        .count()
        + (1 if body.predicted_winner == market.team_b else 0)
    )
    total = total_a + total_b
    if total > 0:
        market.odds_a = round((total_a / total) * 100, 1)
        market.odds_b = round((total_b / total) * 100, 1)

    user.predictions_count += 1
    db.commit()
    db.refresh(pred)
    db.close()
    return {
        "id": pred.id,
        "user_id": pred.user_id,
        "market_id": pred.market_id,
        "predicted_winner": pred.predicted_winner,
        "amount": pred.amount,
    }


@app.get("/api/predictions")
def list_predictions(user_id: Optional[int] = None, market_id: Optional[int] = None):
    db = next(get_db())
    q = db.query(Prediction)
    if user_id is not None:
        q = q.filter(Prediction.user_id == user_id)
    if market_id is not None:
        q = q.filter(Prediction.market_id == market_id)
    preds = q.all()
    result = [
        {
            "id": p.id,
            "user_id": p.user_id,
            "market_id": p.market_id,
            "predicted_winner": p.predicted_winner,
            "amount": p.amount,
            "created_at": p.created_at.isoformat(),
        }
        for p in preds
    ]
    db.close()
    return {"predictions": result}


@app.get("/api/leaderboard")
def leaderboard(limit: int = 10):
    db = next(get_db())
    users = db.query(User).order_by(User.points.desc()).limit(limit).all()
    result = [
        {
            "id": u.id,
            "username": u.username,
            "points": u.points,
            "predictions_count": u.predictions_count,
        }
        for u in users
    ]
    db.close()
    return {"leaderboard": result}


@app.get("/api/stats")
def stats():
    db = next(get_db())
    total_markets = db.query(Market).count()
    total_predictions = db.query(Prediction).count()
    total_users = db.query(User).count()
    total_volume = db.query(Market).with_entities(Market.volume).all()
    volume_sum = round(sum(v[0] for v in total_volume), 2)
    open_markets = db.query(Market).filter(Market.status == "open").count()
    db.close()
    return {
        "total_markets": total_markets,
        "total_predictions": total_predictions,
        "total_users": total_users,
        "total_volume": volume_sum,
        "open_markets": open_markets,
    }


@app.get("/")
def index(request: Request):
    db = next(get_db())
    markets = db.query(Market).all()
    users = db.query(User).order_by(User.points.desc()).limit(10).all()
    total_volume = db.query(Market).with_entities(Market.volume).all()
    total_volume_sum = round(sum(v[0] for v in total_volume), 2)
    total_predictions = db.query(Prediction).count()
    db.close()

    market_list = [
        {
            "id": m.id,
            "title": m.title,
            "team_a": m.team_a,
            "team_b": m.team_b,
            "odds_a": m.odds_a,
            "odds_b": m.odds_b,
            "volume": m.volume,
            "prediction_count": m.prediction_count,
            "status": m.status,
        }
        for m in markets
    ]
    leaderboard_list = [
        {
            "username": u.username,
            "points": u.points,
            "predictions_count": u.predictions_count,
        }
        for u in users
    ]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "markets": market_list,
            "leaderboard": leaderboard_list,
            "total_volume": total_volume_sum,
            "total_predictions": total_predictions,
            "total_markets": len(market_list),
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
