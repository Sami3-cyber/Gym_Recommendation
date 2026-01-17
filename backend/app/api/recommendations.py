"""
Recommendations API Router
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import joblib

router = APIRouter()

# Path to the exercise dataset and model
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "data", "megaGymDataset.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models", "recommendation_model.joblib")


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


def load_exercises() -> pd.DataFrame:
    """Load exercises from CSV file"""
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()
    
    df = pd.read_csv(DATA_PATH)
    # Clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    return df


def create_feature_text(row) -> str:
    """Create combined feature text for TF-IDF"""
    parts = []
    
    if pd.notna(row.get('title')):
        parts.append(str(row['title']))
    if pd.notna(row.get('desc')):
        parts.append(str(row['desc']))
    if pd.notna(row.get('type')):
        parts.append(str(row['type']))
    if pd.notna(row.get('bodypart')):
        parts.append(str(row['bodypart']))
    if pd.notna(row.get('equipment')):
        parts.append(str(row['equipment']))
    if pd.notna(row.get('level')):
        parts.append(str(row['level']))
    
    return ' '.join(parts).lower()


class RecommendationEngine:
    """Content-based recommendation engine"""
    
    def __init__(self):
        self.df = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.is_fitted = False
    
    def fit(self, df: pd.DataFrame):
        """Fit the recommendation model"""
        self.df = df.copy()
        
        # Create feature text
        self.df['feature_text'] = self.df.apply(create_feature_text, axis=1)
        
        # Create TF-IDF matrix
        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)
        )
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.df['feature_text'])
        self.is_fitted = True
    
    def recommend(
        self,
        body_part: Optional[str] = None,
        equipment: Optional[str] = None,
        level: Optional[str] = None,
        exercise_type: Optional[str] = None,
        limit: int = 10,
        exclude_exercises: Optional[List[str]] = None
    ) -> List[dict]:
        """Get exercise recommendations based on filters"""
        
        if not self.is_fitted:
            df = load_exercises()
            if df.empty:
                return []
            self.fit(df)
        
        # Start with all exercises
        mask = pd.Series([True] * len(self.df))
        
        # Apply filters
        if body_part:
            mask &= self.df['bodypart'].str.lower() == body_part.lower()
        if equipment:
            mask &= self.df['equipment'].str.lower() == equipment.lower()
        if level:
            mask &= self.df['level'].str.lower() == level.lower()
        if exercise_type:
            mask &= self.df['type'].str.lower() == exercise_type.lower()
        if exclude_exercises:
            exclude_lower = [e.lower() for e in exclude_exercises]
            mask &= ~self.df['title'].str.lower().isin(exclude_lower)
        
        filtered_df = self.df[mask]
        
        if filtered_df.empty:
            return []
        
        # Create user query from filters
        query_parts = []
        if body_part:
            query_parts.append(body_part)
        if equipment:
            query_parts.append(equipment)
        if level:
            query_parts.append(level)
        if exercise_type:
            query_parts.append(exercise_type)
        
        if query_parts:
            query = ' '.join(query_parts).lower()
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # Calculate similarity for filtered exercises
            filtered_indices = filtered_df.index.tolist()
            filtered_matrix = self.tfidf_matrix[filtered_indices]
            similarities = cosine_similarity(query_vector, filtered_matrix)[0]
            
            # Add similarity scores
            filtered_df = filtered_df.copy()
            filtered_df['similarity'] = similarities
            
            # Sort by similarity and rating
            filtered_df = filtered_df.sort_values(
                by=['similarity', 'rating'],
                ascending=[False, False]
            )
        else:
            # No filters, sort by rating
            filtered_df = filtered_df.copy()
            filtered_df['similarity'] = 1.0
            filtered_df = filtered_df.sort_values(by='rating', ascending=False)
        
        # Limit results
        filtered_df = filtered_df.head(limit)
        
        # Convert to list of dicts
        results = []
        for idx, row in filtered_df.iterrows():
            results.append({
                'id': idx,
                'title': row.get('title', ''),
                'description': row.get('desc', ''),
                'type': row.get('type', ''),
                'body_part': row.get('bodypart', ''),
                'equipment': row.get('equipment', ''),
                'level': row.get('level', ''),
                'rating': row.get('rating') if pd.notna(row.get('rating')) else None,
                'similarity_score': round(row.get('similarity', 0), 4)
            })
        
        return results


# Global recommendation engine instance
recommendation_engine = RecommendationEngine()


@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get personalized exercise recommendations based on user preferences
    """
    recommendations = recommendation_engine.recommend(
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


@router.post("/similar/{exercise_id}")
async def get_similar_exercises(exercise_id: int, limit: int = 5):
    """
    Get exercises similar to a given exercise
    """
    if not recommendation_engine.is_fitted:
        df = load_exercises()
        if df.empty:
            raise HTTPException(status_code=404, detail="No exercise data available")
        recommendation_engine.fit(df)
    
    df = recommendation_engine.df
    
    if exercise_id < 0 or exercise_id >= len(df):
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    # Get similarity for the given exercise
    exercise_vector = recommendation_engine.tfidf_matrix[exercise_id]
    similarities = cosine_similarity(exercise_vector, recommendation_engine.tfidf_matrix)[0]
    
    # Get top similar exercises (excluding itself)
    similar_indices = similarities.argsort()[::-1][1:limit+1]
    
    results = []
    for idx in similar_indices:
        row = df.iloc[idx]
        results.append({
            'id': int(idx),
            'title': row.get('title', ''),
            'description': row.get('desc', ''),
            'type': row.get('type', ''),
            'body_part': row.get('bodypart', ''),
            'equipment': row.get('equipment', ''),
            'level': row.get('level', ''),
            'rating': row.get('rating') if pd.notna(row.get('rating')) else None,
            'similarity_score': round(float(similarities[idx]), 4)
        })
    
    return {"similar_exercises": results}
