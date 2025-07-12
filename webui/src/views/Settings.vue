<template>
  <div class="settings-container" style="background:var(--bt-bg-dark);min-height:100vh;padding:32px 0;">
    <main class="settings-content" style="max-width:900px;margin:0 auto;">
      <div class="page-header" style="text-align:center;margin-bottom:32px;">
        <h1 class="section-title">Einstellungen</h1>
        <p style="color:var(--bt-text-muted);">Verwalten Sie Ihre Kontoeinstellungen</p>
      </div>
      <div v-if="loading" style="text-align:center;padding:48px;">
        <span class="material-icons" style="font-size:38px;color:var(--bt-orange);">hourglass_empty</span>
        <p style="color:var(--bt-text-muted);">Lade Einstellungen...</p>
      </div>
      <div v-else-if="error" style="text-align:center;padding:48px;">
        <span class="material-icons" style="font-size:38px;color:#ff4b4b;">error</span>
        <p style="color:#ff4b4b;">{{ error }}</p>
        <BaseButton @click="loadSettings">Erneut versuchen</BaseButton>
      </div>
      <div v-else style="display:grid;grid-template-columns:1fr 1fr;gap:24px;">
        <BaseCard style="flex-direction:column;align-items:flex-start;">
          <h3 class="section-title">Profil-Einstellungen</h3>
          <div class="form-group" style="margin-bottom:10px;width:100%;">
            <label style="color:var(--bt-orange);">Telegram ID</label>
            <input type="text" v-model="profile.telegram_id" disabled style="width:100%;padding:10px 14px;border-radius:8px;border:none;background:#232632;color:var(--bt-text-white);margin-top:4px;" />
          </div>
          <div class="form-group" style="margin-bottom:10px;width:100%;">
            <label style="color:var(--bt-orange);">Benutzername</label>
            <input type="text" v-model="profile.user_name" style="width:100%;padding:10px 14px;border-radius:8px;border:none;background:#232632;color:var(--bt-text-white);margin-top:4px;" />
          </div>
          <div class="form-group" style="margin-bottom:10px;width:100%;">
            <label style="color:var(--bt-orange);">Telefonnummer</label>
            <input type="tel" v-model="profile.phone" style="width:100%;padding:10px 14px;border-radius:8px;border:none;background:#232632;color:var(--bt-text-white);margin-top:4px;" />
          </div>
          <BaseButton @click="updateProfile">Profil aktualisieren</BaseButton>
        </BaseCard>
        <BaseCard style="flex-direction:column;align-items:flex-start;">
          <h3 class="section-title">Benachrichtigungen</h3>
          <div class="form-group" style="margin-bottom:10px;width:100%;">
            <label class="checkbox-label" style="color:var(--bt-orange);">
              <input type="checkbox" v-model="notifications.signal_notifications" />
              <span>Signal-Benachrichtigungen</span>
            </label>
          </div>
          <div class="form-group" style="margin-bottom:10px;width:100%;">
            <label class="checkbox-label" style="color:var(--bt-orange);">
              <input type="checkbox" v-model="notifications.payment_notifications" />
              <span>Zahlungs-Benachrichtigungen</span>
            </label>
          </div>
          <div class="form-group" style="margin-bottom:10px;width:100%;">
            <label class="checkbox-label" style="color:var(--bt-orange);">
              <input type="checkbox" v-model="notifications.system_notifications" />
              <span>System-Benachrichtigungen</span>
            </label>
          </div>
          <BaseButton @click="updateNotifications">Benachrichtigungen speichern</BaseButton>
        </BaseCard>
        <BaseCard style="flex-direction:column;align-items:flex-start;">
          <h3 class="section-title">Sicherheit</h3>
          <div class="form-group" style="margin-bottom:10px;width:100%;">
            <label class="checkbox-label" style="color:var(--bt-orange);">
              <input type="checkbox" v-model="security.two_factor_enabled" />
              <span>Zwei-Faktor-Authentifizierung</span>
            </label>
          </div>
          <div class="form-group" style="margin-bottom:10px;width:100%;">
            <label class="checkbox-label" style="color:var(--bt-orange);">
              <input type="checkbox" v-model="security.session_timeout" />
              <span>Automatische Session-Timeouts</span>
            </label>
          </div>
          <BaseButton @click="updateSecurity">Sicherheitseinstellungen speichern</BaseButton>
        </BaseCard>
        <BaseCard style="flex-direction:column;align-items:flex-start;">
          <h3 class="section-title">Konto-Aktionen</h3>
          <BaseButton @click="exportData">Daten exportieren</BaseButton>
          <BaseButton style="background:#ff4b4b;color:#fff;" @click="deleteAccount">Konto löschen</BaseButton>
          <BaseButton style="background:#888;color:#fff;" @click="logout">Abmelden</BaseButton>
        </BaseCard>
      </div>
      <div style="margin-top:32px;text-align:center;">
        <BaseButton style="background:#888;color:#fff;" @click="$router.push('/dashboard')">
  <span class="material-icons" style="vertical-align:middle;margin-right:4px;">arrow_back</span>Zurück zum Dashboard
</BaseButton>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'
import BaseCard from '../components/BaseCard.vue'
import BaseButton from '../components/BaseButton.vue'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const error = ref(null)

const profile = ref({
  telegram_id: '',
  user_name: '',
  phone: ''
})

const notifications = ref({
  signal_notifications: true,
  payment_notifications: true,
  system_notifications: true
})

const security = ref({
  two_factor_enabled: false,
  session_timeout: true
})

const loadSettings = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await api.get('/users/profile')
    profile.value = {
      telegram_id: response.data.telegram_id || '',
      user_name: response.data.user_name || '',
      phone: response.data.phone || ''
    }
    
    // Lade Benutzer-Einstellungen
    const settingsResponse = await api.get('/users/settings')
    if (settingsResponse.data) {
      notifications.value = settingsResponse.data.notifications || notifications.value
      security.value = settingsResponse.data.security || security.value
    }
    
    console.log('✅ Einstellungen geladen:', response.data)
  } catch (err) {
    console.error('❌ Fehler beim Laden der Einstellungen:', err)
    // Fallback: Verwende Standard-Werte wenn API nicht verfügbar
    profile.value = {
      telegram_id: 'Nicht verfügbar',
      user_name: 'Nicht verfügbar',
      phone: 'Nicht verfügbar'
    }
    error.value = null // Kein Fehler anzeigen, verwende Fallback
  } finally {
    loading.value = false
  }
}

const updateProfile = async () => {
  try {
    await api.put('/users/profile', profile.value)
    console.log('✅ Profil aktualisiert')
  } catch (err) {
    console.error('❌ Fehler beim Aktualisieren des Profils:', err)
    error.value = 'Fehler beim Aktualisieren des Profils.'
  }
}

const updateNotifications = async () => {
  try {
    await api.put('/users/settings/notifications', notifications.value)
    console.log('✅ Benachrichtigungen aktualisiert')
  } catch (err) {
    console.error('❌ Fehler beim Aktualisieren der Benachrichtigungen:', err)
    error.value = 'Fehler beim Aktualisieren der Benachrichtigungen.'
  }
}

const updateSecurity = async () => {
  try {
    await api.put('/users/settings/security', security.value)
    console.log('✅ Sicherheitseinstellungen aktualisiert')
  } catch (err) {
    console.error('❌ Fehler beim Aktualisieren der Sicherheitseinstellungen:', err)
    error.value = 'Fehler beim Aktualisieren der Sicherheitseinstellungen.'
  }
}

const exportData = async () => {
  try {
    const response = await api.get('/users/export-data')
    const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'user-data.json'
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    console.error('❌ Fehler beim Exportieren der Daten:', err)
    error.value = 'Fehler beim Exportieren der Daten.'
  }
}

const deleteAccount = async () => {
  if (confirm('Sind Sie sicher, dass Sie Ihr Konto löschen möchten? Diese Aktion kann nicht rückgängig gemacht werden.')) {
    try {
      await api.delete('/users/account')
      localStorage.removeItem('wallstreet_session')
      router.push('/login')
    } catch (err) {
      console.error('❌ Fehler beim Löschen des Kontos:', err)
      error.value = 'Fehler beim Löschen des Kontos.'
    }
  }
}

const logout = async () => {
  try {
    await api.post('/auth/logout')
  } catch (err) {
    console.error('❌ Fehler beim Abmelden:', err)
  } finally {
    localStorage.removeItem('wallstreet_session')
    router.push('/login')
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
/* Alle alten Styles entfernt, alles läuft über globale Styles */
</style> 