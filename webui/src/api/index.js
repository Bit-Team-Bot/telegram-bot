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
  
  // Userbot
  USERBOT_START: '/start',
  USERBOT_VERIFY: '/verify',
  USERBOT_DIALOGS: '/api/dialogs',
  USERBOT_CREATE_GROUP: '/api/create_group',
  USERBOT_SEND_MESSAGE: '/api/send_message',
  USERBOT_ADD_USER: '/api/add_user_to_group',
  USERBOT_TRANSFER_OWNERSHIP: '/api/transfer_ownership',
  USERBOT_STATUS: '/status',
  
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
  
  async requestCode(phone, telegram_id = null, use_userbot = true) {
    const payload = { phone, use_userbot }
    if (telegram_id) {
      payload.telegram_id = telegram_id
    }
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
  
  // Userbot API
  async userbotStart(phone) {
    try {
      const response = await axios.post(`${USERBOT_API_URL}${API_ENDPOINTS.USERBOT_START}`, { phone }, {
        timeout: 15000,
        headers: { 'Content-Type': 'application/json' }
      })
      return response.data
    } catch (error) {
      console.error('Userbot Start Error:', error)
      throw new Error('Userbot-Service nicht erreichbar. Verwende Backend-Fallback.')
    }
  },
  
  async userbotVerify(phone, code) {
    try {
      const response = await axios.post(`${USERBOT_API_URL}${API_ENDPOINTS.USERBOT_VERIFY}`, { phone, code }, {
        timeout: 15000,
        headers: { 'Content-Type': 'application/json' }
      })
      return response.data
    } catch (error) {
      console.error('Userbot Verify Error:', error)
      throw new Error('Userbot-Verifizierung fehlgeschlagen. Verwende Backend-Fallback.')
    }
  },
  
  async userbotGetDialogs() {
    const response = await axios.get(`${USERBOT_API_URL}${API_ENDPOINTS.USERBOT_DIALOGS}`)
    return response.data
  },
  
  async userbotCreateGroup(title, supergroup = false) {
    const response = await axios.post(`${USERBOT_API_URL}${API_ENDPOINTS.USERBOT_CREATE_GROUP}`, { title, supergroup })
    return response.data
  },
  
  async userbotSendMessage(groupId, message) {
    const response = await axios.post(`${USERBOT_API_URL}${API_ENDPOINTS.USERBOT_SEND_MESSAGE}`, { group_id: groupId, message })
    return response.data
  },
  
  async userbotAddUserToGroup(userId, groupId) {
    const response = await axios.post(`${USERBOT_API_URL}${API_ENDPOINTS.USERBOT_ADD_USER}`, { user_id: userId, group_id: groupId })
    return response.data
  },
  
  async userbotTransferOwnership(groupId, newOwnerId) {
    const response = await axios.post(`${USERBOT_API_URL}${API_ENDPOINTS.USERBOT_TRANSFER_OWNERSHIP}`, { group_id: groupId, new_owner_id: newOwnerId })
    return response.data
  },
  
  async userbotGetStatus() {
    const response = await axios.get(`${USERBOT_API_URL}${API_ENDPOINTS.USERBOT_STATUS}`)
    return response.data
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
  start: api.userbotStart,
  verify: api.userbotVerify,
  getDialogs: api.userbotGetDialogs,
  createGroup: api.userbotCreateGroup,
  sendMessage: api.userbotSendMessage,
  addUserToGroup: api.userbotAddUserToGroup,
  transferOwnership: api.userbotTransferOwnership,
  getStatus: api.userbotGetStatus,
  
  // Neue Funktionen für automatisierten Session-Flow
  async requestCode(phone) {
    try {
      console.log('🔧 Userbot: Sende Verifizierungscode für:', phone)
      const response = await axios.post(`${USERBOT_API_URL}/start`, { phone }, {
        timeout: 15000,
        headers: { 'Content-Type': 'application/json' }
      })
      console.log('✅ Userbot: Code erfolgreich gesendet:', response.data)
      return response.data
    } catch (error) {
      console.error('❌ Userbot: Fehler beim Senden des Codes:', error)
      throw new Error(`Userbot-Code-Versand fehlgeschlagen: ${error.response?.data?.message || error.message}`)
    }
  },
  
  async verifyCode(phone, code) {
    try {
      console.log('🔧 Userbot: Verifiziere Code für:', phone)
      const response = await axios.post(`${USERBOT_API_URL}/verify`, { phone, code }, {
        timeout: 15000,
        headers: { 'Content-Type': 'application/json' }
      })
      console.log('✅ Userbot: Code erfolgreich verifiziert:', response.data)
      return response.data
    } catch (error) {
      console.error('❌ Userbot: Fehler bei Code-Verifizierung:', error)
      throw new Error(`Userbot-Code-Verifizierung fehlgeschlagen: ${error.response?.data?.message || error.message}`)
    }
  },
  
  async getSessionStatus(phone) {
    try {
      const response = await axios.get(`${USERBOT_API_URL}/status`, {
        timeout: 10000,
        headers: { 'Content-Type': 'application/json' }
      })
      return response.data
    } catch (error) {
      console.error('❌ Userbot: Fehler beim Abrufen des Status:', error)
      throw new Error('Userbot-Status nicht verfügbar')
    }
  },
  
  async stopSession() {
    try {
      const response = await axios.post(`${USERBOT_API_URL}/stop`, {}, {
        timeout: 10000,
        headers: { 'Content-Type': 'application/json' }
      })
      return response.data
    } catch (error) {
      console.error('❌ Userbot: Fehler beim Stoppen der Session:', error)
      throw new Error('Userbot-Session konnte nicht gestoppt werden')
    }
  }
}

export default api
