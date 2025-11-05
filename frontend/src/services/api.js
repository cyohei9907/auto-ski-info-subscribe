import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

// CSRF token取得関数
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Cookie送信を有効化
});

// Request interceptor to add auth token and CSRF token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    
    // CSRF tokenを追加 (POSTなどの変更系リクエストの場合)
    if (['post', 'put', 'patch', 'delete'].includes(config.method.toLowerCase())) {
      const csrfToken = getCookie('csrftoken');
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
      }
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