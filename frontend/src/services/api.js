import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/auth/login/', credentials),
  register: (userData) => api.post('/auth/register/', userData),
  logout: () => api.post('/auth/logout/'),
  getProfile: () => api.get('/auth/profile/'),
  updateProfile: (data) => api.patch('/auth/profile/', data),
  getUser: () => api.get('/auth/user/'),
};

// X Monitor API
export const monitorAPI = {
  getAccounts: () => api.get('/monitor/accounts/'),
  addAccount: (username) => api.post('/monitor/accounts/', { username }),
  updateAccount: (id, data) => api.patch(`/monitor/accounts/${id}/`, data),
  deleteAccount: (id) => api.delete(`/monitor/accounts/${id}/`),
  monitorNow: (id) => api.post(`/monitor/accounts/${id}/monitor/`),
  
  getTweets: (params) => api.get('/monitor/tweets/', { params }),
  analyzeTweet: (id) => api.post(`/monitor/tweets/${id}/analyze/`),
  
  getLogs: () => api.get('/monitor/logs/'),
  getNotifications: () => api.get('/monitor/notifications/'),
  markNotificationRead: (id) => api.post(`/monitor/notifications/${id}/read/`),
};

// AI Service API
export const aiAPI = {
  analyzeSentiment: (text) => api.post('/ai/sentiment/', { text }),
  summarizeText: (text) => api.post('/ai/summarize/', { text }),
  extractTopics: (text) => api.post('/ai/topics/', { text }),
};

export default api;