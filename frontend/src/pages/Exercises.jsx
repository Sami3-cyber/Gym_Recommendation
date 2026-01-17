import { useState, useEffect } from 'react';
import { exercisesApi } from '../services/api';
import ExerciseCard from '../components/ExerciseCard';

function Exercises() {
    const [exercises, setExercises] = useState([]);
    const [filters, setFilters] = useState({
        bodyParts: [],
        equipment: [],
        levels: [],
        types: []
    });

    const [selectedFilters, setSelectedFilters] = useState({
        body_part: '',
        equipment: '',
        level: '',
        exercise_type: ''
    });

    const [page, setPage] = useState(1);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);
    const pageSize = 12;

    useEffect(() => {
        loadFilters();
    }, []);

    useEffect(() => {
        loadExercises();
    }, [page, selectedFilters]);

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

    const loadExercises = async () => {
        setLoading(true);
        try {
            const params = {
                page,
                page_size: pageSize,
                ...Object.fromEntries(
                    Object.entries(selectedFilters).filter(([_, v]) => v !== '')
                )
            };

            const data = await exercisesApi.getExercises(params);
            setExercises(data.exercises || []);
            setTotal(data.total || 0);
        } catch (err) {
            console.error('Error loading exercises:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleFilterChange = (e) => {
        const { name, value } = e.target;
        setSelectedFilters(prev => ({
            ...prev,
            [name]: value
        }));
        setPage(1); // Reset to first page when filtering
    };

    const handleClearFilters = () => {
        setSelectedFilters({
            body_part: '',
            equipment: '',
            level: '',
            exercise_type: ''
        });
        setPage(1);
    };

    const totalPages = Math.ceil(total / pageSize);

    return (
        <div className="page-container">
            <section className="hero">
                <h1>Browse All Exercises</h1>
                <p>
                    Explore our comprehensive database of gym exercises
                </p>
            </section>

            <div className="filters">
                <div className="form-group">
                    <label htmlFor="body_part">Body Part</label>
                    <select
                        id="body_part"
                        name="body_part"
                        className="form-control"
                        value={selectedFilters.body_part}
                        onChange={handleFilterChange}
                    >
                        <option value="">All body parts</option>
                        {filters.bodyParts.map(bp => (
                            <option key={bp} value={bp}>{bp}</option>
                        ))}
                    </select>
                </div>

                <div className="form-group">
                    <label htmlFor="equipment">Equipment</label>
                    <select
                        id="equipment"
                        name="equipment"
                        className="form-control"
                        value={selectedFilters.equipment}
                        onChange={handleFilterChange}
                    >
                        <option value="">All equipment</option>
                        {filters.equipment.map(eq => (
                            <option key={eq} value={eq}>{eq}</option>
                        ))}
                    </select>
                </div>

                <div className="form-group">
                    <label htmlFor="level">Level</label>
                    <select
                        id="level"
                        name="level"
                        className="form-control"
                        value={selectedFilters.level}
                        onChange={handleFilterChange}
                    >
                        <option value="">All levels</option>
                        {filters.levels.map(lv => (
                            <option key={lv} value={lv}>{lv}</option>
                        ))}
                    </select>
                </div>

                <div className="form-group">
                    <label htmlFor="exercise_type">Type</label>
                    <select
                        id="exercise_type"
                        name="exercise_type"
                        className="form-control"
                        value={selectedFilters.exercise_type}
                        onChange={handleFilterChange}
                    >
                        <option value="">All types</option>
                        {filters.types.map(tp => (
                            <option key={tp} value={tp}>{tp}</option>
                        ))}
                    </select>
                </div>

                <div className="form-group" style={{ display: 'flex', alignItems: 'flex-end' }}>
                    <button className="btn btn-secondary" onClick={handleClearFilters}>
                        Clear Filters
                    </button>
                </div>
            </div>

            <div className="results-header">
                <h2>Exercises</h2>
                <span className="results-count">{total} exercises found</span>
            </div>

            {loading ? (
                <div className="loading">
                    <div className="spinner"></div>
                </div>
            ) : exercises.length > 0 ? (
                <>
                    <div className="card-grid">
                        {exercises.map((exercise) => (
                            <ExerciseCard key={exercise.id} exercise={exercise} />
                        ))}
                    </div>

                    {totalPages > 1 && (
                        <div className="pagination">
                            <button
                                onClick={() => setPage(p => Math.max(1, p - 1))}
                                disabled={page === 1}
                            >
                                ← Previous
                            </button>

                            {[...Array(Math.min(5, totalPages))].map((_, i) => {
                                let pageNum;
                                if (totalPages <= 5) {
                                    pageNum = i + 1;
                                } else if (page <= 3) {
                                    pageNum = i + 1;
                                } else if (page >= totalPages - 2) {
                                    pageNum = totalPages - 4 + i;
                                } else {
                                    pageNum = page - 2 + i;
                                }

                                return (
                                    <button
                                        key={pageNum}
                                        className={page === pageNum ? 'active' : ''}
                                        onClick={() => setPage(pageNum)}
                                    >
                                        {pageNum}
                                    </button>
                                );
                            })}

                            <button
                                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                                disabled={page === totalPages}
                            >
                                Next →
                            </button>
                        </div>
                    )}
                </>
            ) : (
                <div className="empty-state">
                    <div className="empty-state-icon">🏋️</div>
                    <p>No exercises found matching your filters.</p>
                    <button className="btn btn-primary" onClick={handleClearFilters}>
                        Clear Filters
                    </button>
                </div>
            )}
        </div>
    );
}

export default Exercises;
