import { useState, useEffect } from 'react';
import { exercisesApi, recommendationsApi } from '../services/api';
import ExerciseCard from '../components/ExerciseCard';

function Recommend() {
    const [filters, setFilters] = useState({
        bodyParts: [],
        equipment: [],
        levels: [],
        types: []
    });

    const [preferences, setPreferences] = useState({
        body_part: '',
        equipment: '',
        level: '',
        exercise_type: '',
        limit: 10
    });

    const [recommendations, setRecommendations] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [hasSearched, setHasSearched] = useState(false);

    useEffect(() => {
        loadFilters();
    }, []);

    const loadFilters = async () => {
        try {
            const data = await exercisesApi.getFilters();
            setFilters({
                bodyParts: data.body_parts || [],
                equipment: data.equipment || [],
                levels: data.levels || [],
                types: data.types || []
            });
        } catch (err) {
            console.error('Error loading filters:', err);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setPreferences(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setHasSearched(true);

        try {
            // Filter out empty values
            const filteredPrefs = Object.fromEntries(
                Object.entries(preferences).filter(([_, v]) => v !== '')
            );

            const data = await recommendationsApi.getRecommendations(filteredPrefs);
            setRecommendations(data.recommendations || []);
        } catch (err) {
            setError('Failed to get recommendations. Please try again.');
            console.error('Error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleClear = () => {
        setPreferences({
            body_part: '',
            equipment: '',
            level: '',
            exercise_type: '',
            limit: 10
        });
        setRecommendations([]);
        setHasSearched(false);
        setError(null);
    };

    return (
        <div className="page-container">
            <section className="hero">
                <h1>Get Personalized Recommendations</h1>
                <p>
                    Tell us about your preferences and we'll recommend the perfect exercises for you
                </p>
            </section>

            <div className="recommendation-form">
                <h2>Your Preferences</h2>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="body_part">Target Body Part</label>
                        <select
                            id="body_part"
                            name="body_part"
                            className="form-control"
                            value={preferences.body_part}
                            onChange={handleInputChange}
                        >
                            <option value="">Any body part</option>
                            {filters.bodyParts.map(bp => (
                                <option key={bp} value={bp}>{bp}</option>
                            ))}
                        </select>
                    </div>

                    <div className="form-group">
                        <label htmlFor="equipment">Equipment Available</label>
                        <select
                            id="equipment"
                            name="equipment"
                            className="form-control"
                            value={preferences.equipment}
                            onChange={handleInputChange}
                        >
                            <option value="">Any equipment</option>
                            {filters.equipment.map(eq => (
                                <option key={eq} value={eq}>{eq}</option>
                            ))}
                        </select>
                    </div>

                    <div className="form-group">
                        <label htmlFor="level">Experience Level</label>
                        <select
                            id="level"
                            name="level"
                            className="form-control"
                            value={preferences.level}
                            onChange={handleInputChange}
                        >
                            <option value="">Any level</option>
                            {filters.levels.map(lv => (
                                <option key={lv} value={lv}>{lv}</option>
                            ))}
                        </select>
                    </div>

                    <div className="form-group">
                        <label htmlFor="exercise_type">Exercise Type</label>
                        <select
                            id="exercise_type"
                            name="exercise_type"
                            className="form-control"
                            value={preferences.exercise_type}
                            onChange={handleInputChange}
                        >
                            <option value="">Any type</option>
                            {filters.types.map(tp => (
                                <option key={tp} value={tp}>{tp}</option>
                            ))}
                        </select>
                    </div>

                    <div className="form-group">
                        <label htmlFor="limit">Number of Recommendations</label>
                        <select
                            id="limit"
                            name="limit"
                            className="form-control"
                            value={preferences.limit}
                            onChange={handleInputChange}
                        >
                            <option value={5}>5 exercises</option>
                            <option value={10}>10 exercises</option>
                            <option value={15}>15 exercises</option>
                            <option value={20}>20 exercises</option>
                        </select>
                    </div>

                    <div className="btn-group" style={{ marginTop: '1.5rem' }}>
                        <button type="submit" className="btn btn-primary" disabled={loading}>
                            {loading ? 'Finding exercises...' : 'Get Recommendations'}
                        </button>
                        <button type="button" className="btn btn-secondary" onClick={handleClear}>
                            Clear
                        </button>
                    </div>
                </form>
            </div>

            {error && (
                <div className="empty-state" style={{ color: '#f56565' }}>
                    <p>{error}</p>
                </div>
            )}

            {hasSearched && !loading && (
                <section className="results-section">
                    <div className="results-header">
                        <h2>Recommended Exercises</h2>
                        <span className="results-count">{recommendations.length} exercises found</span>
                    </div>

                    {recommendations.length > 0 ? (
                        <div className="card-grid">
                            {recommendations.map((exercise) => (
                                <ExerciseCard
                                    key={exercise.id}
                                    exercise={exercise}
                                    showSimilarity={true}
                                />
                            ))}
                        </div>
                    ) : (
                        <div className="empty-state">
                            <div className="empty-state-icon">🔍</div>
                            <p>No exercises found matching your criteria.</p>
                            <p>Try adjusting your filters.</p>
                        </div>
                    )}
                </section>
            )}

            {loading && (
                <div className="loading">
                    <div className="spinner"></div>
                </div>
            )}
        </div>
    );
}

export default Recommend;
