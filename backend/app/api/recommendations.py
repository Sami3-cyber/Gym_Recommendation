"""
Recommendations API Router
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import os
import joblib
import pandas as pd

# Import the shared model class
from app.ml.recommendation_model import GymRecommendationModel

router = APIRouter()

# Path to the exercise dataset and model
def get_data_path():
    # Priority 1: Docker/Production path (ml_data in app root)
    docker_path = os.path.join(os.getcwd(), "ml_data", "megaGymDataset.csv")
    if os.path.exists(docker_path):
        return docker_path
    
    # Priority 2: Local development path (relative to this file)
    local_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "data", "megaGymDataset.csv")
    if os.path.exists(local_path):
        return local_path
        
    return local_path

def get_model_path():
    # Priority 1: CI/CD Downloaded Path (inside app/ml/models)
    # The CI workflow downloads it to backend/app/ml/models/
    # And Docker copies backend/ to /app/
    ci_path = os.path.join(os.path.dirname(__file__), "..", "ml", "models", "recommendation_model.joblib")
    if os.path.exists(ci_path):
        return ci_path

    # Priority 2: Docker volume mount (if using volumes)
    docker_vol_path = os.path.join(os.getcwd(), "ml_models", "recommendation_model.joblib")
    if os.path.exists(docker_vol_path):
        return docker_vol_path
        
    # Priority 3: Local development path
    local_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models", "recommendation_model.joblib")
    if os.path.exists(local_path):
        return local_path
        
    return local_path

DATA_PATH = get_data_path()
MODEL_PATH = get_model_path()


class RecommendationRequest(BaseModel):
    """Request model for recommendations"""
    body_part: Optional[str] = Field(None, description="Target body part (e.g., 'Chest', 'Abdominals')")
    equipment: Optional[str] = Field(None, description="Available equipment (e.g., 'Barbell', 'Dumbbell')")
    level: Optional[str] = Field(None, description="Experience level ('Beginner', 'Intermediate', 'Expert')")
    exercise_type: Optional[str] = Field(None, description="Exercise type ('Strength', 'Stretching', 'Cardio')")
    limit: int = Field(10, ge=1, le=50, description="Number of recommendations to return")
    exclude_exercises: Optional[List[str]] = Field(None, description="Exercise titles to exclude")


class RecommendedExercise(BaseModel):
    """Recommended exercise model"""
    id: int
    title: str
    description: Optional[str] = None
    type: Optional[str] = None
    body_part: Optional[str] = None
    equipment: Optional[str] = None
    level: Optional[str] = None
    rating: Optional[float] = None
    similarity_score: float


class RecommendationResponse(BaseModel):
    """Response model for recommendations"""
    recommendations: List[RecommendedExercise]
    total_found: int
    filters_applied: dict


# Initialize model
recommendation_model = GymRecommendationModel()

def initialize_model():
    """Initialize the model by loading from disk or fitting on data"""
    try:
        if os.path.exists(MODEL_PATH):
            print(f"Loading model from {MODEL_PATH}")
            recommendation_model.load(MODEL_PATH)
        else:
            print(f"Model file not found at {MODEL_PATH}. Training new model...")
            if os.path.exists(DATA_PATH):
                df = pd.read_csv(DATA_PATH)
                # Clean column names
                df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
                recommendation_model.fit(df)
            else:
                print(f"Data file not found at {DATA_PATH}. Model initialization failed.")
    except Exception as e:
        print(f"Error initializing model: {e}")
        # Fallback to training
        if os.path.exists(DATA_PATH):
             print("Fallback: Training model on data...")
             df = pd.read_csv(DATA_PATH)
             df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
             recommendation_model.fit(df)

# Initialize on module load
initialize_model()


@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get personalized exercise recommendations based on user preferences
    """
    if not recommendation_model.is_fitted:
        # Try to initialize again
        initialize_model()
        if not recommendation_model.is_fitted:
             raise HTTPException(status_code=500, detail="Recommendation model could not be initialized")

    try:
        recommendations = recommendation_model.recommend(
            body_part=request.body_part,
            equipment=request.equipment,
            level=request.level,
            exercise_type=request.exercise_type,
            limit=request.limit,
            exclude_exercises=request.exclude_exercises
        )
        
        recommended_exercises = [
            RecommendedExercise(**rec) for rec in recommendations
        ]
        
        filters_applied = {
            "body_part": request.body_part,
            "equipment": request.equipment,
            "level": request.level,
            "exercise_type": request.exercise_type
        }
        
        return RecommendationResponse(
            recommendations=recommended_exercises,
            total_found=len(recommended_exercises),
            filters_applied={k: v for k, v in filters_applied.items() if v is not None}
        )
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/similar/{exercise_id}")
async def get_similar_exercises(exercise_id: int, limit: int = 5):
    """
    Get exercises similar to a given exercise
    """
    if not recommendation_model.is_fitted:
         initialize_model()
         if not recommendation_model.is_fitted:
            raise HTTPException(status_code=500, detail="Recommendation model not initialized")
    
    try:
        results = recommendation_model.get_similar_exercises(exercise_id, limit)
        return {"similar_exercises": results}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error getting similar exercises: {e}")
        raise HTTPException(status_code=500, detail=str(e))
