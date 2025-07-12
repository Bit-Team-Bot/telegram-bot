// src/api/index.js
import axios from 'axios'

// API-Konfiguration für Telegram Bot Management System
// Öffentliche URLs für Internet-Zugriff
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://api.bit-team-bot.online'
const USERBOT_API_URL = import.meta.env.VITE_USERBOT_URL || 'https://userbot.bit-team-bot.online'

// API-Endpunkte
export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  LOGOUT: '/auth/logout',
  REFRESH: '/auth/refresh',
  VERIFY: '/auth/verify',
  
  // Userbot (Multi-User)
  USERBOT_CREATE_SESSION: '/userbot/create-session',
  USERBOT_SEND_CODE: '/userbot/send-code',
  USERBOT_VERIFY_CODE: '/userbot/verify-code',
  USERBOT_SESSION_STATUS: '/userbot/session-status',
  USERBOT_DISCONNECT_SESSION: '/userbot/disconnect-session',
  USERBOT_GET_CHATS: '/userbot/chats',
  USERBOT_CLEANUP_SESSIONS: '/userbot/cleanup-inactive-sessions',
  USERBOT_ACTIVE_SESSIONS_COUNT: '/userbot/active-sessions-count',
  USERBOT_ALL_SESSIONS: '/userbot/all-sessions',
  USERBOT_MY_SESSIONS: '/userbot/my-sessions',
  USERBOT_SESSIONS: '/userbot/sessions',
  
  // Admin
  ADMIN_USERS: '/admin/users',
  ADMIN_STATS: '/admin/stats',
  ADMIN_SETTINGS: '/admin/settings',
  
  // Packages
  PACKAGES: '/packages',
  
  // Payments
  PAYMENTS: '/payments',
  PAYMENT_HISTORY: '/payments/history',
  
  // Users
  USERS: '/users',
  USER_PROFILE: '/users/profile',
  
  // Monitoring
  MONITORING: '/monitoring',
  MONITORING_STATS: '/monitoring/stats',
  
  // Wallet
  WALLET: '/wallet',
  WALLET_BALANCE: '/wallet/balance',
  WALLET_TRANSACTIONS: '/wallet/transactions',
  
  // Health
  HEALTH: '/health',
  STATUS: '/status'
}

// API-Klient mit Axios
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true
})

// Request Interceptor für Auth-Token
apiClient.interceptors.request.use(
  (config) => {
    // Versuche zuerst den Token aus wallstreet_session zu lesen
    const session = localStorage.getItem('wallstreet_session')
    let token = null
    
    if (session) {
      try {
        const sessionData = JSON.parse(session)
        token = sessionData.token
      } catch (e) {
        console.error('Fehler beim Parsen der Session:', e)
      }
    }
    
    // Fallback auf auth_token (für Kompatibilität)
    if (!token) {
      token = localStorage.getItem('auth_token')
    }
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response Interceptor für Token-Refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      // Versuche Auto-Login mit Session-Token
      const session = localStorage.getItem('wallstreet_session')
      if (session) {
        try {
          const sessionData = JSON.parse(session)
          if (sessionData.telegram_id && sessionData.session_token) {
            const response = await axios.post(`${API_BASE_URL}/auth/auto-login`, {
              telegram_id: sessionData.telegram_id,
              session_token: sessionData.session_token
            })
            
            if (response.data.success) {
              // Neue Session-Daten speichern
              localStorage.setItem('wallstreet_session', JSON.stringify({
                token: response.data.access_token,
                user_id: response.data.user.id,
                telegram_id: response.data.user.telegram_id,
                phone: response.data.user.phone,
                package_id: response.data.user.package_id,
                is_superadmin: response.data.user.is_superadmin,
                user_name: response.data.user.user_name,
                session_token: response.data.session.session_token,
                session_expires_at: response.data.session.expires_at,
              }))
              
              // Request mit neuem Token wiederholen
              originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`
          return apiClient(originalRequest)
            }
          }
        } catch (refreshError) {
          console.error('Auto-Login fehlgeschlagen:', refreshError)
        }
      }
      
      // Fallback: User ausloggen
      localStorage.removeItem('wallstreet_session')
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

// API-Funktionen
export const api = {
  // Auth
  async login(credentials) {
    const response = await apiClient.post(API_ENDPOINTS.LOGIN, credentials)
    return response.data
  },
  
  async register(userData) {
    const response = await apiClient.post(API_ENDPOINTS.REGISTER, userData)
    return response.data
  },
  
  async logout() {
    const response = await apiClient.post(API_ENDPOINTS.LOGOUT)
    return response.data
  },
  
  async verifyToken() {
    const response = await apiClient.get(API_ENDPOINTS.VERIFY)
    return response.data
  },
  
  async requestCode(phone, telegram_id = null) {
    const payload = { phone }
    if (telegram_id) {
      payload.telegram_id = telegram_id
    }
    // use_userbot NICHT setzen, damit Backend-Default (false) greift
    const response = await apiClient.post('/auth/request-code', payload)
    return response.data
  },
  
  // Telefonnummer-Verknüpfung
  async linkPhoneToTelegram(telegram_id, phone) {
    const response = await apiClient.post('/users/link_phone', {
      telegram_id,
      phone
    })
    return response.data
  },
  
  // Userbot API (Multi-User)
  async userbotCreateSession(phoneNumber) {
    try {
      const response = await axios.post(`${USERBOT_API_URL}${API_ENDPOINTS.USERBOT_CREATE_SESSION}`, { 
        phone_number: phoneNumber 
      }, {
        timeout: 15000,
        headers: { 'Content-Type': 'application/json' }
      })
      return response.data
    } catch (error) {
      console.error('Userbot Create Session Error:', error)
      throw new Error('Userbot-Service nicht erreichbar.')
    }
  },
  
  async userbotSendCode(phoneNumber) {
    try {
      const response = await axios.post(`${USERBOT_API_URL}${API_ENDPOINTS.USERBOT_SEND_CODE}`, { 
        phone_number: phoneNumber 
      }, {
        timeout: 15000,
        headers: { 'Content-Type': 'application/json' }
      })
      return response.data
    } catch (error) {
      console.error('Userbot Send Code Error:', error)
      throw new Error('Userbot-Code-Versand fehlgeschlagen.')
    }
  },
  
  async userbotVerifyCode(phoneNumber, code, password = null) {
    try {
      const payload = { 
        phone_number: phoneNumber,
        code: code
      }
      
      // Nur password hinzufügen, wenn es nicht null/undefined ist
      if (password !== null && password !== undefined) {
        payload.password = password
      }
      
      const response = await axios.post(`${USERBOT_API_URL}${API_ENDPOINTS.USERBOT_VERIFY_CODE}`, payload, {
        timeout: 15000,
        headers: { 'Content-Type': 'application/json' }
      })
    return response.data
    } catch (error) {
      console.error('Userbot Verify Code Error:', error)
      throw new Error('Userbot-Code-Verifizierung fehlgeschlagen.')
    }
  },
  
  async userbotGetSessionStatus(phoneNumber) {
    try {
      const response = await axios.get(`${USERBOT_API_URL}${API_ENDPOINTS.USERBOT_SESSION_STATUS}/${phoneNumber}`, {
        timeout: 10000,
        headers: { 'Content-Type': 'application/json' }
      })
    return response.data
    } catch (error) {
      console.error('Userbot Session Status Error:', error)
      throw new Error('Userbot-Session-Status nicht verfügbar.')
    }
  },
  
  async userbotDisconnectSession(phoneNumber) {
    try {
      const response = await axios.post(`${USERBOT_API_URL}${API_ENDPOINTS.USERBOT_DISCONNECT_SESSION}`, { 
        phone_number: phoneNumber 
      }, {
        timeout: 10000,
        headers: { 'Content-Type': 'application/json' }
      })
    return response.data
    } catch (error) {
      console.error('Userbot Disconnect Session Error:', error)
      throw new Error('Userbot-Session-Trennung fehlgeschlagen.')
    }
  },
  
  async userbotGetChats(phoneNumber) {
    try {
      const response = await axios.get(`${USERBOT_API_URL}${API_ENDPOINTS.USERBOT_GET_CHATS}/${phoneNumber}`, {
        timeout: 10000,
        headers: { 'Content-Type': 'application/json' }
      })
    return response.data
    } catch (error) {
      console.error('Userbot Get Chats Error:', error)
      throw new Error('Userbot-Chats nicht verfügbar.')
    }
  },
  
  async userbotGetActiveSessionsCount() {
    try {
      const response = await axios.get(`${USERBOT_API_URL}${API_ENDPOINTS.USERBOT_ACTIVE_SESSIONS_COUNT}`, {
        timeout: 10000,
        headers: { 'Content-Type': 'application/json' }
      })
    return response.data
    } catch (error) {
      console.error('Userbot Active Sessions Count Error:', error)
      throw new Error('Userbot-Sessions-Count nicht verfügbar.')
    }
  },
  
  async userbotGetAllSessions() {
    try {
      const response = await axios.get(`${USERBOT_API_URL}${API_ENDPOINTS.USERBOT_ALL_SESSIONS}`, {
        timeout: 10000,
        headers: { 'Content-Type': 'application/json' }
      })
    return response.data
    } catch (error) {
      console.error('Userbot All Sessions Error:', error)
      throw new Error('Userbot-Sessions nicht verfügbar.')
    }
  },
  
  async userbotGetMySessions() {
    try {
      const response = await apiClient.get(API_ENDPOINTS.USERBOT_MY_SESSIONS)
      return response.data
    } catch (error) {
      console.error('Userbot My Sessions Error:', error)
      throw new Error('Userbot-My-Sessions nicht verfügbar.')
    }
  },
  
  // Admin
  async getUsers() {
    const response = await apiClient.get(API_ENDPOINTS.ADMIN_USERS)
    return response.data
  },
  
  async getStats() {
    const response = await apiClient.get(API_ENDPOINTS.ADMIN_STATS)
    return response.data
  },
  
  // Packages
  async getPackages() {
    const response = await apiClient.get(API_ENDPOINTS.PACKAGES)
    return response.data
  },
  
  // Payments
  async getPayments() {
    const response = await apiClient.get(API_ENDPOINTS.PAYMENTS)
    return response.data
  },
  
  async getPaymentHistory() {
    const response = await apiClient.get(API_ENDPOINTS.PAYMENT_HISTORY)
    return response.data
  },
  
  // Users
  async getUserProfile() {
    const response = await apiClient.get(API_ENDPOINTS.USER_PROFILE)
    return response.data
  },
  
  // Wallet
  async getWalletBalance() {
    const response = await apiClient.get(API_ENDPOINTS.WALLET_BALANCE)
    return response.data
  },
  
  async getWalletTransactions() {
    const response = await apiClient.get(API_ENDPOINTS.WALLET_TRANSACTIONS)
    return response.data
  },
  
  // Monitoring
  async getMonitoringStats() {
    const response = await apiClient.get(API_ENDPOINTS.MONITORING_STATS)
    return response.data
  },
  
  // Health
  async getHealth() {
    const response = await apiClient.get(API_ENDPOINTS.HEALTH)
    return response.data
  },
  
  async getStatus() {
    const response = await apiClient.get(API_ENDPOINTS.STATUS)
    return response.data
  },

  // Userbot-Session im eigenen Backend speichern
  async saveUserbotSession(sessionData) {
    // Erwartet: { phone, session_name, session_type, telegram_session_string, is_active }
    const response = await apiClient.post(API_ENDPOINTS.USERBOT_SESSIONS, sessionData)
    return response.data
  },

  // Neue Funktion für klassisches Web-Login
  async verifyWebLoginCode(phone, code) {
    try {
      const payload = { phone, code }
      const response = await apiClient.post('/auth/verify-code', payload)
      return response.data
    } catch (error) {
      console.error('Web-Login Code-Verifizierung fehlgeschlagen:', error)
      // Versuche Backend-Fehlermeldung durchzureichen
      if (error.response && error.response.data && error.response.data.detail) {
        throw new Error(error.response.data.detail)
      }
      throw error
    }
  }
}

export const authAPI = {
  login: api.login,
  register: api.register,
  logout: api.logout,
  verifyToken: api.verifyToken,
  requestCode: api.requestCode
}

export const userbotAPI = {
  // Neue Multi-User-Funktionen
  createSession: api.userbotCreateSession,
  sendCode: api.userbotSendCode,
  verifyCode: api.userbotVerifyCode,
  getSessionStatus: api.userbotGetSessionStatus,
  disconnectSession: api.userbotDisconnectSession,
  getChats: api.userbotGetChats,
  getActiveSessionsCount: api.userbotGetActiveSessionsCount,
  getAllSessions: api.userbotGetAllSessions,
  getMySessions: api.userbotGetMySessions,
  
  // Legacy-Funktionen für Kompatibilität (werden auf neue Endpunkte umgeleitet)
  async requestCode(phone) {
    try {
      console.log('🔧 Userbot: Erstelle Session für:', phone)
      const sessionResult = await api.userbotCreateSession(phone)
      
      if (sessionResult.success) {
      console.log('🔧 Userbot: Sende Verifizierungscode für:', phone)
        const codeResult = await api.userbotSendCode(phone)
        
        if (codeResult.success) {
          console.log('✅ Userbot: Code erfolgreich gesendet:', codeResult)
          return { status: 'code_sent', phone: phone, message: 'Telegram-Code wurde an Ihre Nummer gesendet' }
        } else {
          throw new Error(codeResult.error || 'Code-Versand fehlgeschlagen')
        }
      } else {
        throw new Error(sessionResult.error || 'Session-Erstellung fehlgeschlagen')
      }
    } catch (error) {
      console.error('❌ Userbot: Fehler beim Senden des Codes:', error)
      throw new Error(`Userbot-Code-Versand fehlgeschlagen: ${error.message}`)
    }
  },
  
  async verifyCode(phone, code) {
    try {
      console.log('🔧 Userbot: Verifiziere Code für:', phone)
      const result = await api.userbotVerifyCode(phone, code)
      
      if (result.success) {
        console.log('✅ Userbot: Code erfolgreich verifiziert:', result)
        return { status: 'success', message: 'Code erfolgreich verifiziert' }
      } else {
        throw new Error(result.error || 'Code-Verifizierung fehlgeschlagen')
      }
    } catch (error) {
      console.error('❌ Userbot: Fehler bei Code-Verifizierung:', error)
      throw new Error(`Userbot-Code-Verifizierung fehlgeschlagen: ${error.message}`)
    }
  },
  
  async getSessionStatus(phone) {
    try {
      const result = await api.userbotGetSessionStatus(phone)
      return result
    } catch (error) {
      console.error('❌ Userbot: Fehler beim Abrufen des Status:', error)
      throw new Error('Userbot-Status nicht verfügbar')
    }
  }
}

export default api
