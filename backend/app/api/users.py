"""
Users API Router with Supabase Integration
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import uuid4
from app.db import supabase

router = APIRouter()

# --- Models ---

class UserCreate(BaseModel):
    """User creation model"""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    experience_level: Optional[str] = Field(None, description="Beginner, Intermediate, or Expert")
    fitness_goals: Optional[List[str]] = Field(None, description="List of fitness goals")
    available_equipment: Optional[List[str]] = Field(None, description="List of available equipment")


class User(BaseModel):
    """User model"""
    id: str
    email: str
    name: str
    experience_level: Optional[str] = None
    fitness_goals: Optional[List[str]] = None
    available_equipment: Optional[List[str]] = None
    created_at: str


class UserUpdate(BaseModel):
    """User update model"""
    name: Optional[str] = None
    experience_level: Optional[str] = None
    fitness_goals: Optional[List[str]] = None
    available_equipment: Optional[List[str]] = None


class FavoriteCreate(BaseModel):
    """Favorite creation model"""
    exercise_title: str


class Favorite(BaseModel):
    """Favorite model"""
    id: str
    user_id: str
    exercise_title: str
    created_at: str


class HistoryCreate(BaseModel):
    """History creation model"""
    exercise_title: str
    notes: Optional[str] = None


class History(BaseModel):
    """History model"""
    id: str
    user_id: str
    exercise_title: str
    completed_at: str
    notes: Optional[str] = None


# --- Helpers ---

def get_db():
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available (Check SUPABASE_URL/KEY)")
    return supabase


# --- User Endpoints ---

@router.post("/", response_model=User)
async def create_user(user: UserCreate):
    db = get_db()
    
    # Check if email exists
    existing = db.table("users").select("id").eq("email", user.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid4())
    new_user = {
        "id": user_id,
        "email": user.email,
        "name": user.name,
        "experience_level": user.experience_level,
        "fitness_goals": user.fitness_goals or [],
        "available_equipment": user.available_equipment or [],
        "created_at": datetime.now().isoformat()
    }
    
    try:
        res = db.table("users").insert(new_user).execute()
        # Return the created object implies verify it was made
        if not res.data:
             raise HTTPException(status_code=500, detail="Failed to create user")
        return User(**res.data[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str):
    db = get_db()
    
    res = db.table("users").select("*").eq("id", user_id).execute()
    
    if not res.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(**res.data[0])


@router.put("/{user_id}", response_model=User)
async def update_user(user_id: str, user_update: UserUpdate):
    db = get_db()
    
    # Check existence
    existing = db.table("users").select("id").eq("id", user_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    
    if not update_data:
        return User(**db.table("users").select("*").eq("id", user_id).execute().data[0])
        
    try:
        res = db.table("users").update(update_data).eq("id", user_id).execute()
        return User(**res.data[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    db = get_db()
    
    # Check existence
    existing = db.table("users").select("id").eq("id", user_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="User not found")
        
    try:
        # Cascading delete usually handled by SQL, but explicit is okay too if configured
        db.table("users").delete().eq("id", user_id).execute()
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Favorites Endpoints ---

@router.get("/{user_id}/favorites", response_model=List[Favorite])
async def get_favorites(user_id: str):
    db = get_db()
    
    res = db.table("favorites").select("*").eq("user_id", user_id).execute()
    return [Favorite(**fav) for fav in res.data]


@router.post("/{user_id}/favorites", response_model=Favorite)
async def add_favorite(user_id: str, favorite: FavoriteCreate):
    db = get_db()
    
    # Check duplications using unique constraint or query
    existing = db.table("favorites").select("id").eq("user_id", user_id).eq("exercise_title", favorite.exercise_title).execute()
    if existing.data:
         raise HTTPException(status_code=400, detail="Exercise already in favorites")

    new_favorite = {
        "id": str(uuid4()),
        "user_id": user_id,
        "exercise_title": favorite.exercise_title,
        "created_at": datetime.now().isoformat()
    }
    
    try:
        res = db.table("favorites").insert(new_favorite).execute()
        return Favorite(**res.data[0])
    except Exception as e:
        # Likely foreign key violation if user doesn't exist
        if "foreign key constraint" in str(e).lower():
             raise HTTPException(status_code=404, detail="User not found")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}/favorites/{favorite_id}")
async def remove_favorite(user_id: str, favorite_id: str):
    db = get_db()
    
    res = db.table("favorites").delete().eq("id", favorite_id).eq("user_id", user_id).execute()
    
    if not res.data:
        raise HTTPException(status_code=404, detail="Favorite not found")
        
    return {"message": "Favorite removed successfully"}


# --- History Endpoints ---

@router.get("/{user_id}/history", response_model=List[History])
async def get_history(user_id: str):
    db = get_db()
    res = db.table("history").select("*").eq("user_id", user_id).order("completed_at", desc=True).execute()
    return [History(**h) for h in res.data]


@router.post("/{user_id}/history", response_model=History)
async def add_history(user_id: str, history: HistoryCreate):
    db = get_db()
    
    new_history = {
        "id": str(uuid4()),
        "user_id": user_id,
        "exercise_title": history.exercise_title,
        "completed_at": datetime.now().isoformat(),
        "notes": history.notes
    }
    
    try:
        res = db.table("history").insert(new_history).execute()
        return History(**res.data[0])
    except Exception as e:
        if "foreign key constraint" in str(e).lower():
             raise HTTPException(status_code=404, detail="User not found")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}/history/{history_id}")
async def remove_history(user_id: str, history_id: str):
    db = get_db()
    
    res = db.table("history").delete().eq("id", history_id).eq("user_id", user_id).execute()
    
    if not res.data:
        raise HTTPException(status_code=404, detail="History entry not found")
        
    return {"message": "History entry removed successfully"}
