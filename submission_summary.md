# NBA Playoffs Prediction Market — Submission Summary

## Project Name
NBA Playoffs Prediction Market

## Description
A decentralized prediction market platform for NBA playoff series, deployed on Polygon. Users browse active playoff series, view real-time odds, submit winner predictions, and compete on a live leaderboard. Pre-seeded with 8 first-round series (East & West conferences).

## Tech Stack
- **Backend:** Python, FastAPI
- **Database:** SQLAlchemy (SQLite for MVP, upgradeable to PostgreSQL)
- **Frontend:** Jinja2 templates with dark-themed CSS
- **Blockchain:** Polygon ecosystem (prepared for smart contract integration)
- **Tools:** Uvicorn, Pydantic, python-dotenv

## How to Run
```bash
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Winning Angle
Decentralized NBA playoff prediction market on Polygon featuring:
- Real-time odds adjustments based on crowd predictions
- Live leaderboard gamifying predictor performance
- Polygon ecosystem alignment for low-fee, fast on-chain settlements
- Expandable to smart contracts for transparent payout execution

## Hackathon URL
https://dorahacks.io/hackathon/nba-prediction-market

## Deadline
June 1, 2026
