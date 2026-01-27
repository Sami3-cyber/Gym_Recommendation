"""
Gym Exercise Recommendation API - Main Entry Point 
and testing pull request
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.api import exercises, recommendations, users

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Gym Exercise Recommendation API",
    description="API for recommending gym exercises based on user preferences",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(exercises.router, prefix="/api/exercises", tags=["Exercises"])
app.include_router(recommendations.router, prefix="/api/recommend", tags=["Recommendations"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])


@app.get("/", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Gym Exercise Recommendation API is running",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def detailed_health():
    """Detailed health check with dependencies status"""
    return {
        "status": "healthy",
        "api": "up",
        "version": "1.0.0"
    }
