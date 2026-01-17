"""
Unit Tests for Gym Exercise Recommendation API
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.ml.recommendation_model import GymRecommendationModel


# Sample test data
SAMPLE_EXERCISES = pd.DataFrame({
    'title': [
        'Barbell Bench Press',
        'Dumbbell Curl',
        'Squat',
        'Deadlift',
        'Push-up'
    ],
    'desc': [
        'A strength exercise for chest',
        'An arm exercise for biceps',
        'A leg exercise for quadriceps',
        'A full body exercise',
        'A bodyweight chest exercise'
    ],
    'type': ['Strength', 'Strength', 'Strength', 'Strength', 'Strength'],
    'bodypart': ['Chest', 'Arms', 'Legs', 'Full Body', 'Chest'],
    'equipment': ['Barbell', 'Dumbbell', 'Barbell', 'Barbell', 'Body Only'],
    'level': ['Intermediate', 'Beginner', 'Intermediate', 'Expert', 'Beginner'],
    'rating': [9.0, 8.5, 9.2, 9.5, 8.0]
})


class TestGymRecommendationModel:
    """Test cases for GymRecommendationModel"""
    
    def test_model_initialization(self):
        """Test that model initializes correctly"""
        model = GymRecommendationModel()
        
        assert model.df is None
        assert model.tfidf_vectorizer is None
        assert model.tfidf_matrix is None
        assert model.is_fitted is False
    
    def test_model_fit(self):
        """Test that model fits correctly on data"""
        model = GymRecommendationModel()
        model.fit(SAMPLE_EXERCISES)
        
        assert model.is_fitted is True
        assert model.df is not None
        assert model.tfidf_vectorizer is not None
        assert model.tfidf_matrix is not None
        assert len(model.df) == 5
    
    def test_model_recommend_with_body_part_filter(self):
        """Test recommendations with body part filter"""
        model = GymRecommendationModel()
        model.fit(SAMPLE_EXERCISES)
        
        recommendations = model.recommend(body_part='Chest', limit=5)
        
        assert len(recommendations) > 0
        for rec in recommendations:
            assert rec['body_part'].lower() == 'chest'
    
    def test_model_recommend_with_level_filter(self):
        """Test recommendations with level filter"""
        model = GymRecommendationModel()
        model.fit(SAMPLE_EXERCISES)
        
        recommendations = model.recommend(level='Beginner', limit=5)
        
        assert len(recommendations) > 0
        for rec in recommendations:
            assert rec['level'].lower() == 'beginner'
    
    def test_model_recommend_empty_result(self):
        """Test that model returns empty list when no matches"""
        model = GymRecommendationModel()
        model.fit(SAMPLE_EXERCISES)
        
        # Use filters that won't match any exercise
        recommendations = model.recommend(
            body_part='NonExistentPart',
            limit=5
        )
        
        assert recommendations == []
    
    def test_model_recommend_limit(self):
        """Test that recommendations respect limit parameter"""
        model = GymRecommendationModel()
        model.fit(SAMPLE_EXERCISES)
        
        recommendations = model.recommend(limit=2)
        
        assert len(recommendations) <= 2
    
    def test_model_recommend_exclude_exercises(self):
        """Test that excluded exercises are not in results"""
        model = GymRecommendationModel()
        model.fit(SAMPLE_EXERCISES)
        
        exclude = ['Barbell Bench Press']
        recommendations = model.recommend(
            body_part='Chest',
            exclude_exercises=exclude,
            limit=5
        )
        
        for rec in recommendations:
            assert rec['title'] not in exclude


class TestRecommendationResponse:
    """Test recommendation response structure"""
    
    def test_recommendation_has_required_fields(self):
        """Test that recommendations have all required fields"""
        model = GymRecommendationModel()
        model.fit(SAMPLE_EXERCISES)
        
        recommendations = model.recommend(limit=1)
        
        assert len(recommendations) > 0
        rec = recommendations[0]
        
        required_fields = ['id', 'title', 'description', 'type', 
                          'body_part', 'equipment', 'level', 
                          'rating', 'similarity_score']
        
        for field in required_fields:
            assert field in rec


class TestSimilarExercises:
    """Test similar exercises functionality"""
    
    def test_get_similar_exercises(self):
        """Test getting similar exercises"""
        model = GymRecommendationModel()
        model.fit(SAMPLE_EXERCISES)
        
        # Get exercises similar to first one (Barbell Bench Press - Chest)
        similar = model.get_similar_exercises(0, limit=3)
        
        assert len(similar) <= 3
        # Push-up should be similar (also Chest)
        titles = [s['title'] for s in similar]
        assert 'Push-up' in titles or len(similar) > 0
    
    def test_similar_exercises_excludes_self(self):
        """Test that similar exercises excludes the query exercise"""
        model = GymRecommendationModel()
        model.fit(SAMPLE_EXERCISES)
        
        similar = model.get_similar_exercises(0, limit=5)
        
        for s in similar:
            assert s['id'] != 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
