"""
ML Model Training Script
Trains the recommendation model and logs to MLFlow
"""
import pandas as pd
import numpy as np
import os
import json
import yaml
import joblib
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from backend/.env
env_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
load_dotenv(env_path)

# Configure MLFlow Authentication for DagsHub
if os.getenv('DAGSHUB_USERNAME') and not os.getenv('MLFLOW_TRACKING_USERNAME'):
    os.environ['MLFLOW_TRACKING_USERNAME'] = os.getenv('DAGSHUB_USERNAME')
    
if os.getenv('DAGSHUB_TOKEN') and not os.getenv('MLFLOW_TRACKING_PASSWORD'):
    os.environ['MLFLOW_TRACKING_PASSWORD'] = os.getenv('DAGSHUB_TOKEN')

import mlflow
import mlflow.sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Import your custom model class
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from app.ml.recommendation_model import GymRecommendationModel


def load_params():
    """Load parameters from params.yaml"""
    params_path = os.path.join(os.path.dirname(__file__), 'params.yaml')
    with open(params_path, 'r') as f:
        return yaml.safe_load(f)


def train_model():
    """Train and save the recommendation model"""
    
    # Load parameters
    params = load_params()
    
    # Load data
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'megaGymDataset.csv')
    df = pd.read_csv(data_path)
    
    print(f"Loaded {len(df)} exercises")
    print(f"Columns: {df.columns.tolist()}")
    
    # Initialize and fit model
    model = GymRecommendationModel()
    model.fit(df)
    
    # Calculate metrics
    metrics = {
        'num_exercises': len(df),
        'vocabulary_size': len(model.tfidf_vectorizer.vocabulary_),
        'matrix_shape': list(model.tfidf_matrix.shape),
        'timestamp': datetime.now().isoformat()
    }
    
    # Test the model
    test_recommendations = model.recommend(body_part='Chest', limit=5)
    metrics['test_recommendations_count'] = len(test_recommendations)
    
    # Save model
    model_path = os.path.join(os.path.dirname(__file__), 'models', 'recommendation_model.joblib')
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    model.save(model_path)
    
    print(f"Model saved to {model_path}")
    
    # Save metrics
    metrics_path = os.path.join(os.path.dirname(__file__), 'metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"Metrics saved to {metrics_path}")
    
    # Log to MLFlow if configured
    if os.getenv('MLFLOW_TRACKING_URI'):
        with mlflow.start_run():
            # Log parameters
            mlflow.log_param('max_features', params['model']['max_features'])
            mlflow.log_param('ngram_range', str(params['model']['ngram_range']))
            mlflow.log_param('num_exercises', len(df))
            
            # Log metrics
            mlflow.log_metric('vocabulary_size', metrics['vocabulary_size'])
            mlflow.log_metric('matrix_rows', metrics['matrix_shape'][0])
            mlflow.log_metric('matrix_cols', metrics['matrix_shape'][1])
            
            # Log model
            # Log model and register it
            mlflow.sklearn.log_model(
                model.tfidf_vectorizer,
                "tfidf_vectorizer",
                registered_model_name="GymRecommendation"
            )
            
            # Log artifacts
            mlflow.log_artifact(model_path)
            mlflow.log_artifact(metrics_path)
            
            print(f"Logged to MLFlow: {mlflow.active_run().info.run_id}")
    
    return model, metrics


if __name__ == '__main__':
    model, metrics = train_model()
    print("\nTraining complete!")
    print(f"Metrics: {json.dumps(metrics, indent=2)}")
