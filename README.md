# NBA Playoffs Prediction Market

Built for the **NBA Playoffs Prediction Market Hackathon** (https://dorahacks.io/hackathon/nba-prediction-market) — a $1,000 prize pool competition on the Polygon ecosystem.

## Description

A decentralized prediction market platform for NBA playoff series. Users can browse active playoff series markets, view real-time odds, submit predictions on series winners, and climb the leaderboard. The platform seeds 8 first-round playoff series (Eastern and Western Conference) with demo data on startup.

Built with Python, FastAPI, SQLAlchemy, and Jinja2 — designed for easy deployment on Polygon.

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
```

## Usage

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open http://localhost:8000 in your browser.

## API Documentation

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Health check |
| `/api/markets` | GET | List all prediction markets |
| `/api/market/{id}` | GET | Get single market with predictions |
| `/api/predictions` | GET | List predictions (filter by `?user_id=` or `?market_id=`) |
| `/api/predictions` | POST | Submit a prediction |
| `/api/leaderboard` | GET | Top predictors (`?limit=10`) |
| `/api/stats` | GET | Platform statistics |

### POST /api/predictions

```json
{
  "user_id": 1,
  "market_id": 1,
  "predicted_winner": "Boston Celtics",
  "amount": 100.0
}
```

## Screenshot

![NBA Playoffs Prediction Market dashboard](screenshot.png)

Dark-themed dashboard showing playoff series cards with odds bars, volume stats, and a leaderboard table of top predictors.
