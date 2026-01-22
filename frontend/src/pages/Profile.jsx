import { useState, useEffect } from 'react';
import { usersApi } from '../services/api';

function Profile() {
    const [user, setUser] = useState(null);
    const [favorites, setFavorites] = useState([]);

    const [isCreating, setIsCreating] = useState(false);
    const [formData, setFormData] = useState({
        email: '',
        name: '',
        experience_level: 'Beginner'
    });
    const [loading, setLoading] = useState(false);

    // Check for saved user in localStorage
    useEffect(() => {
        const savedUserId = localStorage.getItem('gymrec_user_id');
        if (savedUserId) {
            loadUser(savedUserId);
        }
    }, []);

    const loadUser = async (userId) => {
        try {
            const userData = await usersApi.getUser(userId);
            setUser(userData);
            loadFavorites(userId);

        } catch (err) {
            console.error('Error loading user:', err);
            localStorage.removeItem('gymrec_user_id');
        }
    };

    const loadFavorites = async (userId) => {
        try {
            const data = await usersApi.getFavorites(userId);
            setFavorites(data);
        } catch (err) {
            console.error('Error loading favorites:', err);
        }
    };



    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleCreateProfile = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const userData = await usersApi.createUser(formData);
            setUser(userData);
            localStorage.setItem('gymrec_user_id', userData.id);
            setIsCreating(false);
        } catch (err) {
            console.error('Error creating profile:', err);
            alert(`Failed to create profile: ${err.response?.data?.detail || err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('gymrec_user_id');
        setUser(null);
        setFavorites([]);

    };

    const handleRemoveFavorite = async (favoriteId) => {
        try {
            await usersApi.removeFavorite(user.id, favoriteId);
            setFavorites(prev => prev.filter(f => f.id !== favoriteId));
        } catch (err) {
            console.error('Error removing favorite:', err);
        }
    };

    if (!user && !isCreating) {
        return (
            <div className="page-container">
                <section className="hero">
                    <h1>Your Profile</h1>
                    <p>Create a profile to save favorites and track your workout history</p>
                    <button
                        className="btn btn-primary"
                        onClick={() => setIsCreating(true)}
                    >
                        Create Profile
                    </button>
                </section>
            </div>
        );
    }

    if (isCreating) {
        return (
            <div className="page-container">
                <section className="hero">
                    <h1>Create Your Profile</h1>
                </section>

                <div className="recommendation-form">
                    <form onSubmit={handleCreateProfile}>
                        <div className="form-group">
                            <label htmlFor="name">Name</label>
                            <input
                                type="text"
                                id="name"
                                name="name"
                                className="form-control"
                                placeholder="Enter your name"
                                value={formData.name}
                                onChange={handleInputChange}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="email">Email</label>
                            <input
                                type="email"
                                id="email"
                                name="email"
                                className="form-control"
                                placeholder="Enter your email"
                                value={formData.email}
                                onChange={handleInputChange}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="experience_level">Experience Level</label>
                            <select
                                id="experience_level"
                                name="experience_level"
                                className="form-control"
                                value={formData.experience_level}
                                onChange={handleInputChange}
                            >
                                <option value="Beginner">Beginner</option>
                                <option value="Intermediate">Intermediate</option>
                                <option value="Expert">Expert</option>
                            </select>
                        </div>

                        <div className="btn-group" style={{ marginTop: '1.5rem' }}>
                            <button type="submit" className="btn btn-primary" disabled={loading}>
                                {loading ? 'Creating...' : 'Create Profile'}
                            </button>
                            <button
                                type="button"
                                className="btn btn-secondary"
                                onClick={() => setIsCreating(false)}
                            >
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        );
    }

    return (
        <div className="page-container">
            <section className="profile-section">
                <div className="profile-header">
                    <div className="profile-avatar">
                        👤
                    </div>
                    <div className="profile-info">
                        <h2>{user.name}</h2>
                        <p>{user.email}</p>
                        <p>Level: {user.experience_level || 'Not set'}</p>
                    </div>
                    <button className="btn btn-secondary" onClick={handleLogout}>
                        Logout
                    </button>
                </div>

                <div className="card" style={{ marginBottom: '2rem' }}>
                    <h3 style={{ marginBottom: '1rem' }}>⭐ Favorite Exercises</h3>
                    {favorites.length > 0 ? (
                        <ul style={{ listStyle: 'none', padding: 0 }}>
                            {favorites.map(fav => (
                                <li key={fav.id} style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    padding: '0.75rem',
                                    borderBottom: '1px solid var(--border-color)'
                                }}>
                                    <span>{fav.exercise_title}</span>
                                    <button
                                        className="btn btn-secondary"
                                        style={{ padding: '0.25rem 0.75rem', fontSize: '0.875rem' }}
                                        onClick={() => handleRemoveFavorite(fav.id)}
                                    >
                                        Remove
                                    </button>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p style={{ color: 'var(--text-muted)' }}>
                            No favorites yet. Browse exercises and add some!
                        </p>
                    )}
                </div>


            </section>
        </div>
    );
}

export default Profile;
