"""
Gym Exercise Recommendation Model

This module contains the ML model for recommending gym exercises
using content-based filtering with TF-IDF and cosine similarity.
"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os
from typing import Optional, List, Dict, Any

import mlflow
import mlflow.sklearn


class GymRecommendationModel:
    """
    Content-based recommendation model for gym exercises.
    Uses TF-IDF vectorization and cosine similarity.
    """
    
    def __init__(self):
        self.df = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.is_fitted = False
        self.model_version = "1.0.0"
    
    def _create_feature_text(self, row: pd.Series) -> str:
        """Create combined feature text for TF-IDF from a row"""
        parts = []
        
        for col in ['title', 'desc', 'type', 'bodypart', 'equipment', 'level']:
            if col in row.index and pd.notna(row[col]):
                parts.append(str(row[col]))
        
        return ' '.join(parts).lower()
    
    def fit(self, df: pd.DataFrame, log_to_mlflow: bool = False) -> 'GymRecommendationModel':
        """
        Fit the recommendation model on exercise data.
        
        Args:
            df: DataFrame with exercise data
            log_to_mlflow: Whether to log the model to MLFlow
            
        Returns:
            self
        """
        self.df = df.copy()
        
        # Clean column names
        self.df.columns = self.df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        # Create feature text
        self.df['feature_text'] = self.df.apply(self._create_feature_text, axis=1)
        
        # Create TF-IDF vectorizer and matrix
        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95
        )
        
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.df['feature_text'])
        self.is_fitted = True
        
        if log_to_mlflow:
            self._log_to_mlflow()
        
        return self
    
    def _log_to_mlflow(self):
        """Log model parameters and artifacts to MLFlow"""
        mlflow.log_param("max_features", 5000)
        mlflow.log_param("ngram_range", "(1, 2)")
        mlflow.log_param("num_exercises", len(self.df))
        mlflow.log_param("model_version", self.model_version)
        
        mlflow.log_metric("vocabulary_size", len(self.tfidf_vectorizer.vocabulary_))
        mlflow.log_metric("matrix_shape_0", self.tfidf_matrix.shape[0])
        mlflow.log_metric("matrix_shape_1", self.tfidf_matrix.shape[1])
    
    def save(self, model_path: str):
        """Save the model to disk"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before saving")
        
        model_data = {
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'tfidf_matrix': self.tfidf_matrix,
            'df': self.df,
            'model_version': self.model_version
        }
        
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(model_data, model_path)
    
    def load(self, model_path: str) -> 'GymRecommendationModel':
        """Load the model from disk"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        
        model_data = joblib.load(model_path)
        
        self.tfidf_vectorizer = model_data['tfidf_vectorizer']
        self.tfidf_matrix = model_data['tfidf_matrix']
        self.df = model_data['df']
        self.model_version = model_data.get('model_version', '1.0.0')
        self.is_fitted = True
        
        return self
    
    def recommend(
        self,
        body_part: Optional[str] = None,
        equipment: Optional[str] = None,
        level: Optional[str] = None,
        exercise_type: Optional[str] = None,
        limit: int = 10,
        exclude_exercises: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get exercise recommendations based on user preferences.
        
        Args:
            body_part: Target body part
            equipment: Available equipment
            level: Experience level
            exercise_type: Type of exercise
            limit: Maximum number of recommendations
            exclude_exercises: Exercises to exclude
            
        Returns:
            List of recommended exercises with scores
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making recommendations")
        
        # Start with all exercises
        mask = pd.Series([True] * len(self.df), index=self.df.index)
        
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
        
        filtered_df = self.df[mask].copy()
        
        if filtered_df.empty:
            return []
        
        # Create query from filters
        query_parts = [p for p in [body_part, equipment, level, exercise_type] if p]
        
        if query_parts:
            query = ' '.join(query_parts).lower()
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # Get similarity scores
            filtered_indices = filtered_df.index.tolist()
            filtered_matrix = self.tfidf_matrix[filtered_indices]
            similarities = cosine_similarity(query_vector, filtered_matrix)[0]
            
            filtered_df['similarity'] = similarities
            filtered_df = filtered_df.sort_values(
                by=['similarity', 'rating'],
                ascending=[False, False]
            )
        else:
            filtered_df['similarity'] = 1.0
            filtered_df = filtered_df.sort_values(by='rating', ascending=False)
        
        # Return top results
        results = []
        for idx, row in filtered_df.head(limit).iterrows():
            results.append({
                'id': int(idx),
                'title': row.get('title', ''),
                'description': row.get('desc', ''),
                'type': row.get('type', ''),
                'body_part': row.get('bodypart', ''),
                'equipment': row.get('equipment', ''),
                'level': row.get('level', ''),
                'rating': float(row['rating']) if pd.notna(row.get('rating')) else None,
                'similarity_score': round(float(row['similarity']), 4)
            })
        
        return results
    
    def get_similar_exercises(self, exercise_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get exercises similar to a given exercise.
        
        Args:
            exercise_id: ID of the exercise
            limit: Maximum number of similar exercises
            
        Returns:
            List of similar exercises with similarity scores
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        if exercise_id < 0 or exercise_id >= len(self.df):
            raise ValueError(f"Invalid exercise ID: {exercise_id}")
        
        exercise_vector = self.tfidf_matrix[exercise_id]
        similarities = cosine_similarity(exercise_vector, self.tfidf_matrix)[0]
        
        # Get top similar (excluding itself)
        similar_indices = similarities.argsort()[::-1][1:limit+1]
        
        results = []
        for idx in similar_indices:
            row = self.df.iloc[idx]
            results.append({
                'id': int(idx),
                'title': row.get('title', ''),
                'description': row.get('desc', ''),
                'type': row.get('type', ''),
                'body_part': row.get('bodypart', ''),
                'equipment': row.get('equipment', ''),
                'level': row.get('level', ''),
                'rating': float(row['rating']) if pd.notna(row.get('rating')) else None,
                'similarity_score': round(float(similarities[idx]), 4)
            })
        
        return results
