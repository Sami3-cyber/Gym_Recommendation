# Gym Exercise Recommendation System

A full-stack web application that serves a machine learning model for gym exercise recommendations.

## Tech Stack

- **Frontend**: React + Vite
- **Backend**: FastAPI (Python)
- **ML Model**: Content-based recommendation
- **Database**: Supabase (PostgreSQL)
- **ML Registry**: MLFlow on DagsHub
- **Data Versioning**: DVC
- **Containerization**: Docker
- **CI/CD**: GitHub Actions

## Project Structure

```
├── backend/          # FastAPI backend
├── frontend/         # React + Vite frontend
├── ml/               # ML notebooks and data
├── .github/workflows # CI/CD pipelines
└── docker-compose.yml
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker-compose up --build
```

## Environment Variables

Create `.env` files in both `backend/` and `frontend/` directories. See `.env.example` files for required variables.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/exercises` | GET | Get all exercises |
| `/api/recommend` | POST | Get recommendations |
| `/api/users` | POST | Create user |

## License

MIT
