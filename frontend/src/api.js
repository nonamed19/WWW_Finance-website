import axios from 'axios';

// In development Vite proxies this prefix to FastAPI.  A deployed frontend can
// override it with VITE_API_URL (for example, https://api.example.com).
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 15_000,
});

export const authConfig = () => {
  const token = localStorage.getItem('token');
  return token ? { headers: { Authorization: `Token ${token}` } } : {};
};

export const clearSession = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('userInfo');
  localStorage.removeItem('surveyCompleted');
};

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) clearSession();
    return Promise.reject(error);
  },
);

export default api;
