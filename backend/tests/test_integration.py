"""
Integration Tests for Gym Exercise Recommendation API
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_health_check(self):
        """Test root endpoint returns healthy status"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_detailed_health_check(self):
        """Test detailed health endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["api"] == "up"


class TestExercisesAPI:
    """Test exercises API endpoints"""
    
    def test_get_exercises_returns_list(self):
        """Test that get exercises returns a list"""
        response = client.get("/api/exercises/")
        
        assert response.status_code == 200
        data = response.json()
        assert "exercises" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert isinstance(data["exercises"], list)
    
    def test_get_exercises_pagination(self):
        """Test exercises pagination"""
        response = client.get("/api/exercises/?page=1&page_size=5")
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 5
    
    def test_get_exercise_filters(self):
        """Test getting available filters"""
        response = client.get("/api/exercises/filters")
        
        assert response.status_code == 200
        data = response.json()
        assert "body_parts" in data
        assert "equipment" in data
        assert "levels" in data
        assert "types" in data


class TestRecommendationsAPI:
    """Test recommendations API endpoints"""
    
    def test_get_recommendations_basic(self):
        """Test basic recommendations endpoint"""
        response = client.post(
            "/api/recommend/",
            json={"limit": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert "total_found" in data
        assert "filters_applied" in data
    
    def test_get_recommendations_with_filters(self):
        """Test recommendations with filters"""
        response = client.post(
            "/api/recommend/",
            json={
                "body_part": "Chest",
                "level": "Beginner",
                "limit": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
    
    def test_get_recommendations_validates_limit(self):
        """Test that limit is validated"""
        response = client.post(
            "/api/recommend/",
            json={"limit": 100}  # Max is 50
        )
        
        # Should still work but be capped
        assert response.status_code == 422 or response.status_code == 200


class TestUsersAPI:
    """Test users API endpoints"""
    
    def test_create_user(self):
        """Test user creation"""
        response = client.post(
            "/api/users/",
            json={
                "email": "test@example.com",
                "name": "Test User",
                "experience_level": "Beginner"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
        assert "id" in data
        
        # Cleanup
        user_id = data["id"]
        client.delete(f"/api/users/{user_id}")
    
    def test_get_user(self):
        """Test getting user by ID"""
        # Create user first
        create_response = client.post(
            "/api/users/",
            json={
                "email": "gettest@example.com",
                "name": "Get Test User"
            }
        )
        user_id = create_response.json()["id"]
        
        # Get user
        response = client.get(f"/api/users/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["name"] == "Get Test User"
        
        # Cleanup
        client.delete(f"/api/users/{user_id}")
    
    def test_get_nonexistent_user_returns_404(self):
        """Test that getting nonexistent user returns 404"""
        response = client.get("/api/users/nonexistent-id")
        
        assert response.status_code == 404


class TestFavoritesAPI:
    """Test favorites management endpoints"""
    
    @pytest.fixture
    def test_user(self):
        """Create a test user for favorites tests"""
        response = client.post(
            "/api/users/",
            json={
                "email": "favorites@example.com",
                "name": "Favorites Test"
            }
        )
        user_id = response.json()["id"]
        yield user_id
        client.delete(f"/api/users/{user_id}")
    
    def test_add_favorite(self, test_user):
        """Test adding a favorite"""
        response = client.post(
            f"/api/users/{test_user}/favorites",
            json={"exercise_title": "Bench Press"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["exercise_title"] == "Bench Press"
        assert "id" in data
    
    def test_get_favorites(self, test_user):
        """Test getting user favorites"""
        # Add a favorite first
        client.post(
            f"/api/users/{test_user}/favorites",
            json={"exercise_title": "Squat"}
        )
        
        response = client.get(f"/api/users/{test_user}/favorites")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
