"""
End-to-End Tests for Gym Exercise Recommendation API
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app

client = TestClient(app)


# Check if ML model is available for recommendation tests
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'app', 'api', '..', '..', '..', 'ml', 'models', 'recommendation_model.joblib')
MODEL_AVAILABLE = os.path.exists(MODEL_PATH)
skip_if_no_model = pytest.mark.skipif(not MODEL_AVAILABLE, reason="ML model not available in CI")


class TestUserRegistrationFlow:
    """Test complete user registration flow"""
    
    def test_complete_user_registration_flow(self):
        """
        E2E Test 1: User registration and profile management
        1. Create a new user
        2. Retrieve the user profile
        3. Update the user profile
        4. Delete the user
        """
        # Step 1: Create user
        create_response = client.post(
            "/api/users/",
            json={
                "email": "e2e_test@example.com",
                "name": "E2E Test User",
                "experience_level": "Beginner",
                "fitness_goals": ["Build muscle", "Lose weight"],
                "available_equipment": ["Barbell", "Dumbbell"]
            }
        )
        
        assert create_response.status_code == 200
        user = create_response.json()
        user_id = user["id"]
        assert user["name"] == "E2E Test User"
        assert user["experience_level"] == "Beginner"
        
        # Step 2: Retrieve user
        get_response = client.get(f"/api/users/{user_id}")
        
        assert get_response.status_code == 200
        retrieved_user = get_response.json()
        assert retrieved_user["email"] == "e2e_test@example.com"
        
        # Step 3: Update user
        update_response = client.put(
            f"/api/users/{user_id}",
            json={
                "name": "Updated E2E User",
                "experience_level": "Intermediate"
            }
        )
        
        assert update_response.status_code == 200
        updated_user = update_response.json()
        assert updated_user["name"] == "Updated E2E User"
        assert updated_user["experience_level"] == "Intermediate"
        
        # Step 4: Delete user
        delete_response = client.delete(f"/api/users/{user_id}")
        
        assert delete_response.status_code == 200
        
        # Verify deletion
        get_deleted = client.get(f"/api/users/{user_id}")
        assert get_deleted.status_code == 404


class TestExerciseRecommendationFlow:
    """Test complete exercise recommendation flow"""
    
    @skip_if_no_model
    def test_complete_recommendation_flow(self):
        """
        E2E Test 2: Exercise recommendation workflow
        1. Get available filters
        2. Request recommendations with specific filters
        3. Verify recommendations match criteria
        """
        # Step 1: Get available filters
        filters_response = client.get("/api/exercises/filters")
        
        assert filters_response.status_code == 200
        filters = filters_response.json()
        assert "body_parts" in filters
        assert "equipment" in filters
        assert "levels" in filters
        
        # Step 2: Request recommendations
        recommendation_response = client.post(
            "/api/recommend/",
            json={
                "body_part": "Chest",
                "level": "Beginner",
                "limit": 5
            }
        )
        
        assert recommendation_response.status_code == 200
        result = recommendation_response.json()
        assert "recommendations" in result
        assert "filters_applied" in result
        
        # Step 3: Verify recommendations match criteria
        recommendations = result["recommendations"]
        filters_applied = result["filters_applied"]
        
        assert filters_applied.get("body_part") == "Chest"
        assert filters_applied.get("level") == "Beginner"
        
        # Each recommendation should match the filters (if we have data)
        for rec in recommendations:
            if rec["body_part"]:
                assert rec["body_part"].lower() == "chest"
            if rec["level"]:
                assert rec["level"].lower() == "beginner"


class TestFavoritesFlow:
    """Test favorites management flow"""
    
    def test_favorites_flow(self):
        """
        E2E Test 3: Favorites management
        1. Create a user
        2. Add exercises to favorites
        3. Verify favorites list
        4. Clean up
        """
        # Step 1: Create user
        user_response = client.post(
            "/api/users/",
            json={
                "email": "favorites_test@example.com",
                "name": "Favorites Test User"
            }
        )
        
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]
        
        try:
            # Step 2: Add to favorites
            fav1_response = client.post(
                f"/api/users/{user_id}/favorites",
                json={"exercise_title": "Bench Press"}
            )
            assert fav1_response.status_code == 200
            
            fav2_response = client.post(
                f"/api/users/{user_id}/favorites",
                json={"exercise_title": "Squat"}
            )
            assert fav2_response.status_code == 200
            
            # Step 3: Verify favorites
            favorites_response = client.get(f"/api/users/{user_id}/favorites")
            assert favorites_response.status_code == 200
            favorites = favorites_response.json()
            assert len(favorites) >= 2
            
            titles = [f["exercise_title"] for f in favorites]
            assert "Bench Press" in titles
            assert "Squat" in titles
            
        finally:
            # Step 6: Clean up
            client.delete(f"/api/users/{user_id}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
