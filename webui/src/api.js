import axios from "axios"

// API-Konfiguration
const API_BASE_URL = "https://api.bit-team-bot.online";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // Erhöhe Timeout auf 10 Sekunden
  withCredentials: true, // Wichtig für CORS mit Credentials
  headers: {
    'Content-Type': 'application/json',
  }
})

// Request Interceptor für besseres Error Handling und Authorization
api.interceptors.request.use(
  (config) => {
    console.log('🔧 API Request:', config.method?.toUpperCase(), config.url);
    
    // Authorization Header aus localStorage setzen
    const session = localStorage.getItem('wallstreet_session')
    if (session) {
      try {
        const data = JSON.parse(session)
        if (data.token) {
          config.headers.Authorization = `Bearer ${data.token}`
        }
      } catch (error) {
        console.error('❌ Fehler beim Parsen der Session:', error)
      }
    }
    
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response Interceptor für besseres Error Handling
api.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.status, error.response?.data);
    
    // Bei 401 (Unauthorized) automatisch ausloggen
    if (error.response?.status === 401) {
      console.log('🔒 401 Unauthorized - Logge User aus');
      localStorage.removeItem('wallstreet_session');
      // Redirect zur Login-Seite
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

export default api
