import { useState } from 'react';

function ExerciseCard({ exercise, showSimilarity = false, isFavorite = false, onToggle }) {
    const [isExpanded, setIsExpanded] = useState(false);

    const truncateText = (text, maxLength = 100) => {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return isExpanded ? text : text.substring(0, maxLength) + '...';
    };

    return (
        <div className="exercise-card">
            {onToggle && (
                <button
                    className={`favorite-btn ${isFavorite ? 'active' : ''}`}
                    onClick={(e) => {
                        e.stopPropagation();
                        onToggle(exercise);
                    }}
                    title={isFavorite ? "Remove from favorites" : "Add to favorites"}
                >
                    {isFavorite ? '❤️' : '🤍'}
                </button>
            )}
            <h3>{exercise.title}</h3>
            <div className="description-container">
                <p>{truncateText(exercise.description)}</p>
                {exercise.description && exercise.description.length > 100 && (
                    <button
                        className="read-more-btn"
                        onClick={(e) => {
                            e.stopPropagation();
                            setIsExpanded(!isExpanded);
                        }}
                    >
                        {isExpanded ? 'Show Less' : 'Read More'}
                    </button>
                )}
            </div>

            <div className="exercise-meta">
                {exercise.body_part && (
                    <span className="tag body-part">{exercise.body_part}</span>
                )}
                {exercise.equipment && (
                    <span className="tag equipment">{exercise.equipment}</span>
                )}
                {exercise.level && (
                    <span className="tag level">{exercise.level}</span>
                )}
                {exercise.type && (
                    <span className="tag type">{exercise.type}</span>
                )}

                {showSimilarity && exercise.similarity_score !== undefined && (
                    <span className="similarity-score">
                        🎯 {(exercise.similarity_score * 100).toFixed(0)}% match
                    </span>
                )}
            </div>

            {exercise.rating && (
                <div className="rating">
                    <span>⭐</span>
                    <span className="rating-value">{exercise.rating.toFixed(1)}</span>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                        / 10
                    </span>
                </div>
            )}
        </div>
    );
}

export default ExerciseCard;
