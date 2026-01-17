import axios from 'axios';

// API base URL - update this for production
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Exercises API
export const exercisesApi = {
    getExercises: async (params = {}) => {
        const response = await api.get('/api/exercises/', { params });
        return response.data;
    },

    getExercise: async (id) => {
        const response = await api.get(`/api/exercises/${id}`);
        return response.data;
    },

    getFilters: async () => {
        const response = await api.get('/api/exercises/filters');
        return response.data;
    },
};

// Recommendations API
export const recommendationsApi = {
    getRecommendations: async (preferences) => {
        const response = await api.post('/api/recommend/', preferences);
        return response.data;
    },

    getSimilarExercises: async (exerciseId, limit = 5) => {
        const response = await api.post(`/api/recommend/similar/${exerciseId}?limit=${limit}`);
        return response.data;
    },
};

// Users API
export const usersApi = {
    createUser: async (userData) => {
        const response = await api.post('/api/users/', userData);
        return response.data;
    },

    getUser: async (userId) => {
        const response = await api.get(`/api/users/${userId}`);
        return response.data;
    },

    updateUser: async (userId, userData) => {
        const response = await api.put(`/api/users/${userId}`, userData);
        return response.data;
    },

    deleteUser: async (userId) => {
        const response = await api.delete(`/api/users/${userId}`);
        return response.data;
    },

    // Favorites
    getFavorites: async (userId) => {
        const response = await api.get(`/api/users/${userId}/favorites`);
        return response.data;
    },

    addFavorite: async (userId, exerciseTitle) => {
        const response = await api.post(`/api/users/${userId}/favorites`, { exercise_title: exerciseTitle });
        return response.data;
    },

    removeFavorite: async (userId, favoriteId) => {
        const response = await api.delete(`/api/users/${userId}/favorites/${favoriteId}`);
        return response.data;
    },

    // History
    getHistory: async (userId) => {
        const response = await api.get(`/api/users/${userId}/history`);
        return response.data;
    },

    addHistory: async (userId, exerciseTitle, notes = '') => {
        const response = await api.post(`/api/users/${userId}/history`, {
            exercise_title: exerciseTitle,
            notes
        });
        return response.data;
    },
};

// Health check
export const healthCheck = async () => {
    const response = await api.get('/');
    return response.data;
};

export default api;
