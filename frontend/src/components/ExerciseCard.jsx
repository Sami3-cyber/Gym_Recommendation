function ExerciseCard({ exercise, showSimilarity = false }) {
    const truncateText = (text, maxLength = 100) => {
        if (!text) return '';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    };

    return (
        <div className="exercise-card">
            <h3>{exercise.title}</h3>
            <p>{truncateText(exercise.description)}</p>

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
