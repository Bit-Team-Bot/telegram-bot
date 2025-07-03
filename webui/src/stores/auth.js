import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null,
    user_id: null,
    telegram_id: null,
    phone: null,
    package_id: null,
    is_superadmin: false,
    role: 'user',
    user_name: null,
    session_token: null,
    session_expires_at: null,
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    isAuthenticated: (state) => !!state.token,
    isSuperadmin: (state) => state.is_superadmin,
    isPartner: (state) => state.role === 'partner',
    hasValidSession: (state) => {
      if (!state.session_token || !state.session_expires_at) return false
      return new Date(state.session_expires_at) > new Date()
    },
  },
  actions: {
    setToken(token) {
      this.token = token
    },
    setSession(session) {
      this.session_token = session.session_token
      this.session_expires_at = session.expires_at
    },
    async restoreSession() {
      const session = localStorage.getItem('wallstreet_session')
      if (session) {
        const data = JSON.parse(session)
        this.token = data.token
        this.user_id = data.user_id
        this.telegram_id = data.telegram_id
        this.phone = data.phone
        this.package_id = data.package_id
        this.is_superadmin = data.is_superadmin
        this.role = data.role || 'user'
        this.user_name = data.user_name
        this.session_token = data.session_token
        this.session_expires_at = data.session_expires_at
        
        // Prüfe ob Token vorhanden ist (nicht nur Session)
        if (this.token) {
        return true
        } else {
          // Kein Token vorhanden, lösche Session
          this.logout()
          return false
        }
      }
      return false
    },
    async loginSession(data) {
      this.token = data.access_token
      this.user_id = data.user.id
      this.telegram_id = data.user.telegram_id
      this.phone = data.user.phone
      this.package_id = data.user.package_id
      this.is_superadmin = data.user.is_superadmin
      this.role = data.user.role || 'user'
      this.user_name = data.user.user_name
      
      // Session-Daten speichern
      if (data.session) {
        this.session_token = data.session.session_token
        this.session_expires_at = data.session.expires_at
      }
      
      localStorage.setItem('wallstreet_session', JSON.stringify({
        token: this.token,
        user_id: this.user_id,
        telegram_id: this.telegram_id,
        phone: this.phone,
        package_id: this.package_id,
        is_superadmin: this.is_superadmin,
        role: this.role,
        user_name: this.user_name,
        session_token: this.session_token,
        session_expires_at: this.session_expires_at,
      }))
    },
    async login(phone, code) {
      try {
        const response = await api.post('/auth/verify-code', {
          phone: phone,
          code: code
        })
        
        if (response.data.success) {
          await this.loginSession(response.data)
          return { success: true }
        } else {
          return { success: false, error: response.data.detail }
        }
      } catch (error) {
        console.error('Login error:', error)
        return { success: false, error: error.response?.data?.detail || 'Login fehlgeschlagen' }
      }
    },
    async autoLogin(telegram_id) {
      try {
        const payload = { telegram_id }
        
        // Füge Session-Token hinzu, falls vorhanden
        if (this.session_token) {
          payload.session_token = this.session_token
        }
        
        const response = await api.post('/auth/auto-login', payload)
        
        if (response.data.success) {
          await this.loginSession(response.data)
          return { success: true }
        } else {
          return { success: false, error: response.data.detail }
        }
      } catch (error) {
        console.error('Auto-login error:', error)
        return { success: false, error: error.response?.data?.detail || 'Auto-Login fehlgeschlagen' }
      }
    },
    async logout() {
      try {
        // Sende Logout-Request an Backend
        if (this.telegram_id && this.session_token) {
          await api.post('/auth/logout', {
            telegram_id: this.telegram_id,
            session_token: this.session_token
          })
        }
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        // Lokale Daten löschen
      this.token = null
      this.user_id = null
      this.telegram_id = null
      this.phone = null
      this.package_id = null
      this.is_superadmin = false
      this.role = 'user'
      this.user_name = null
        this.session_token = null
        this.session_expires_at = null
      localStorage.removeItem('wallstreet_session')
      }
    }
  }
})
