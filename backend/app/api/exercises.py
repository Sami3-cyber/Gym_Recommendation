"""
Exercises API Router
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
import pandas as pd
import os

router = APIRouter()

# Path to the exercise dataset
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "data", "megaGymDataset.csv")


class Exercise(BaseModel):
    """Exercise model"""
    id: int
    title: str
    description: Optional[str] = None
    type: Optional[str] = None
    body_part: Optional[str] = None
    equipment: Optional[str] = None
    level: Optional[str] = None
    rating: Optional[float] = None
    rating_desc: Optional[str] = None


class ExerciseListResponse(BaseModel):
    """Response model for exercise list"""
    exercises: List[Exercise]
    total: int
    page: int
    page_size: int


def load_exercises() -> pd.DataFrame:
    """Load exercises from CSV file"""
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()
    
    df = pd.read_csv(DATA_PATH)
    # Clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    return df


@router.get("/", response_model=ExerciseListResponse)
async def get_exercises(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    body_part: Optional[str] = Query(None, description="Filter by body part"),
    equipment: Optional[str] = Query(None, description="Filter by equipment"),
    level: Optional[str] = Query(None, description="Filter by level"),
    exercise_type: Optional[str] = Query(None, description="Filter by exercise type")
):
    """
    Get all exercises with pagination and filtering
    """
    df = load_exercises()
    
    if df.empty:
        return ExerciseListResponse(exercises=[], total=0, page=page, page_size=page_size)
    
    # Apply filters
    if body_part:
        df = df[df['bodypart'].str.lower() == body_part.lower()]
    if equipment:
        df = df[df['equipment'].str.lower() == equipment.lower()]
    if level:
        df = df[df['level'].str.lower() == level.lower()]
    if exercise_type:
        df = df[df['type'].str.lower() == exercise_type.lower()]
    
    total = len(df)
    
    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    df_page = df.iloc[start:end]
    
    exercises = []
    for idx, row in df_page.iterrows():
        exercises.append(Exercise(
            id=idx,
            title=row.get('title', ''),
            description=row.get('desc', ''),
            type=row.get('type', ''),
            body_part=row.get('bodypart', ''),
            equipment=row.get('equipment', ''),
            level=row.get('level', ''),
            rating=row.get('rating') if pd.notna(row.get('rating')) else None,
            rating_desc=row.get('ratingdesc', '')
        ))
    
    return ExerciseListResponse(
        exercises=exercises,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/filters")
async def get_filters():
    """
    Get available filter options
    """
    df = load_exercises()
    
    if df.empty:
        return {
            "body_parts": [],
            "equipment": [],
            "levels": [],
            "types": []
        }
    
    return {
        "body_parts": sorted(df['bodypart'].dropna().unique().tolist()),
        "equipment": sorted(df['equipment'].dropna().unique().tolist()),
        "levels": sorted(df['level'].dropna().unique().tolist()),
        "types": sorted(df['type'].dropna().unique().tolist())
    }


@router.get("/{exercise_id}", response_model=Exercise)
async def get_exercise(exercise_id: int):
    """
    Get a specific exercise by ID
    """
    df = load_exercises()
    
    if df.empty or exercise_id < 0 or exercise_id >= len(df):
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    row = df.iloc[exercise_id]
    
    return Exercise(
        id=exercise_id,
        title=row.get('title', ''),
        description=row.get('desc', ''),
        type=row.get('type', ''),
        body_part=row.get('bodypart', ''),
        equipment=row.get('equipment', ''),
        level=row.get('level', ''),
        rating=row.get('rating') if pd.notna(row.get('rating')) else None,
        rating_desc=row.get('ratingdesc', '')
    )
