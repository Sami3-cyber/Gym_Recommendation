import { Link } from 'react-router-dom';

function Home() {
    return (
        <div className="page-container">
            <section className="hero">
                <h1>Find Your Perfect Workout</h1>
                <p>
                    Get personalized gym exercise recommendations powered by machine learning.
                    Whether you're a beginner or expert, we'll help you find the right exercises for your goals.
                </p>
                <div className="btn-group">
                    <Link to="/recommend" className="btn btn-primary">
                        Get Recommendations →
                    </Link>
                    <Link to="/exercises" className="btn btn-secondary">
                        Browse Exercises
                    </Link>
                </div>
            </section>

            <section className="features">
                <div className="feature-card">
                    <div className="feature-icon">🎯</div>
                    <h3>Personalized Recommendations</h3>
                    <p>
                        Our ML model analyzes your preferences and fitness level to suggest
                        exercises tailored just for you.
                    </p>
                </div>

                <div className="feature-card">
                    <div className="feature-icon">💪</div>
                    <h3>2500+ Exercises</h3>
                    <p>
                        Access a comprehensive database of gym exercises covering all muscle groups,
                        equipment types, and difficulty levels.
                    </p>
                </div>

                <div className="feature-card">
                    <div className="feature-icon">📊</div>
                    <h3>Track Your Progress</h3>
                    <p>
                        Save your favorite exercises and keep track of your workout history
                        to monitor your fitness journey.
                    </p>
                </div>

                <div className="feature-card">
                    <div className="feature-icon">🔍</div>
                    <h3>Advanced Filtering</h3>
                    <p>
                        Filter exercises by body part, equipment, difficulty level, and exercise type
                        to find exactly what you need.
                    </p>
                </div>

                <div className="feature-card">
                    <div className="feature-icon">⭐</div>
                    <h3>Community Ratings</h3>
                    <p>
                        See ratings and reviews from other users to help you choose the most
                        effective exercises.
                    </p>
                </div>

                <div className="feature-card">
                    <div className="feature-icon">🚀</div>
                    <h3>Quick Start</h3>
                    <p>
                        No account needed to get started. Simply select your preferences and
                        get instant recommendations.
                    </p>
                </div>
            </section>

            <section className="hero" style={{ marginTop: '3rem' }}>
                <h2>Ready to transform your workouts?</h2>
                <p>Start getting personalized exercise recommendations in seconds.</p>
                <Link to="/recommend" className="btn btn-primary">
                    Start Now →
                </Link>
            </section>
        </div>
    );
}

export default Home;
