<template>
  <div class="login-container">
    <!-- Header direkt in der Login-Komponente -->
    <header class="header-container">
      <div class="header-content">
        <div class="logo-section">
          <img src="@/assets/wallstreet-header.png" alt="Wallstreet Crypto" class="header-logo" />
        </div>
      </div>
    </header>
    
    <div class="login-content">
      <div class="login-card">
        <h2 class="login-title">Telegram Anmeldung</h2>
        <p class="login-subtitle">Melden Sie sich mit Ihrer Telefonnummer an</p>

        <div v-if="error" class="error-box">
          {{ error }}
        </div>

        <div v-if="!codeSent" class="login-form">
          <!-- Schritt 1: Telefonnummer eingeben -->
          <div class="form-group">
            <label for="phone">Telefonnummer</label>
            <input
              id="phone"
              v-model="phone"
              type="tel"
              placeholder="+49 123456789"
              @input="validatePhone"
              :class="{ 'error': phoneError }"
              :disabled="isLoading"
            />
            <span v-if="phoneError" class="error-message">{{ phoneError }}</span>
          </div>

          <!-- Telegram-ID Status -->
          <div v-if="telegramId" class="success-box">
            <h4>✅ Telegram-ID erfasst!</h4>
            <p>Deine Telegram-ID: <code>{{ telegramId }}</code></p>
            <p>Jetzt wird deine Telefonnummer mit deiner Telegram-ID verknüpft.</p>
          </div>

          <div v-if="!telegramId" class="warning-box">
            <h4>⚠️ Keine Telegram-ID gefunden!</h4>
            <p>Du musst zuerst unseren Telegram-Bot starten, um deine Telegram-ID zu erfassen.</p>
            
            <div class="solution-steps">
              <h5>So beheben Sie das Problem:</h5>
              <ol>
                <li>Öffnen Sie unseren Telegram-Bot: <a href="https://t.me/bitteam_bot" target="_blank" class="bot-link">@bitteam_bot</a></li>
                <li>Senden Sie <code>/start</code> an den Bot</li>
                <li>Klicken Sie auf den Button "🌐 Webinterface öffnen"</li>
                <li>Die Telegram-ID wird automatisch übertragen</li>
              </ol>
            </div>
          </div>

          <!-- Verifizierungsmethode wählen -->
          <div v-if="userbotPackageChecked && hasUserbotPackage" class="form-group">
            <label class="checkbox-label">
              <input
                v-model="useUserbot"
                type="checkbox"
                :disabled="isLoading"
              />
              <span>Userbot-Verifizierung verwenden (empfohlen)</span>
            </label>
            <small class="form-help">
              Falls aktiviert, wird die echte Telegram-Verifizierung verwendet. 
              Bei Problemen wird automatisch auf Backend-Verifizierung zurückgegriffen.
            </small>
          </div>
          
          <div v-else-if="userbotPackageChecked && !hasUserbotPackage" class="form-group">
            <div class="info-box">
              <h4>ℹ️ Userbot-Verifizierung nicht verfügbar</h4>
              <p>Sie benötigen ein aktives Userbot-Paket, um die Userbot-Verifizierung zu verwenden.</p>
              <p>Die Anmeldung erfolgt über das Backend-System.</p>
            </div>
          </div>

          <button
            @click="linkPhoneToTelegram"
            :disabled="isLoading || !isPhoneValid || !telegramId"
            class="btn-primary login-button"
          >
            <span v-if="isLoading">Verknüpfe...</span>
            <span v-else>Telefonnummer mit Telegram verknüpfen</span>
          </button>
        </div>

        <div v-else class="login-form">
          <!-- Schritt 2: Code eingeben -->
          <div class="input-group">
            <label for="code" class="input-label">
              Verifizierungscode
            </label>
            <input
              id="code"
              v-model="code"
              type="text"
              placeholder="123456"
              maxlength="6"
              required
              class="input-field code-input"
            />
            <p class="code-info">
              Code wurde an {{ phone }} gesendet
            </p>
          </div>

          <div class="button-group">
            <button
              @click="verifyCode"
              :disabled="isLoading || !code"
              class="btn-primary verify-button"
            >
              <span v-if="isLoading">Verifiziere...</span>
              <span v-else>Code verifizieren</span>
            </button>
            
            <button
              @click="backToPhone"
              :disabled="isLoading"
              class="btn-secondary"
            >
              Zurück
            </button>
          </div>
        </div>

        <!-- Sprachauswahl -->
        <div class="language-selector">
          <label class="language-label">
            Sprache
          </label>
          <select 
            v-model="$i18n.locale" 
            class="language-select"
          >
            <option value="de">Deutsch</option>
            <option value="en">English</option>
          </select>
        </div>

        <!-- Debug-Link -->
        <div class="debug-link">
          <router-link to="/debug" class="debug-link-text">
            🐛 Debug-Informationen
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import { api, userbotAPI } from '../api/index.js'

const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()

const phone = ref('')
const code = ref('')
const codeSent = ref(false)
const phoneError = ref('')
const error = ref('')
const isLoading = ref(false)
const telegramId = ref('')
const useUserbot = ref(true)
const hasUserbotPackage = ref(false)
const userbotPackageChecked = ref(false)

const checkUserbotPackageStatus = async () => {
  try {
    const response = await fetch('/api/user/userbot-package-status', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      hasUserbotPackage.value = data.has_userbot_package
    } else if (response.status === 401) {
      // User ist nicht eingeloggt - das ist normal beim Login
      hasUserbotPackage.value = false
    }
  } catch (error) {
    console.error('Fehler beim Prüfen des Paket-Status:', error)
    hasUserbotPackage.value = false
  } finally {
    userbotPackageChecked.value = true
  }
}

onMounted(async () => {
  console.log('🔍 Starte Telegram-ID-Erkennung...')
  
  // 0. Telegram WebApp initialisieren (falls verfügbar)
  if (window.Telegram && window.Telegram.WebApp) {
    console.log('🔧 Initialisiere Telegram WebApp...')
    try {
      window.Telegram.WebApp.ready()
      console.log('✅ Telegram WebApp bereit gemacht')
    } catch (e) {
      console.warn('⚠️ Konnte Telegram WebApp nicht initialisieren:', e)
    }
  }
  
  // 1. Telegram-ID aus URL-Parameter lesen (Bot-Button)
  const urlParams = new URLSearchParams(window.location.search)
  const userParam = urlParams.get('user')
  const tgidParam = urlParams.get('tgid')
  const telegramIdParam = urlParams.get('telegram_id')
  if (userParam) {
    telegramId.value = userParam
    console.log('📱 Telegram-ID aus URL-Parameter "user" gelesen:', telegramId.value)
  } else if (tgidParam) {
    telegramId.value = tgidParam
    console.log('📱 Telegram-ID aus URL-Parameter "tgid" gelesen:', telegramId.value)
  } else if (telegramIdParam) {
    telegramId.value = telegramIdParam
    console.log('📱 Telegram-ID aus URL-Parameter "telegram_id" gelesen:', telegramId.value)
  } else {
    console.log('❌ Keine Telegram-ID in URL-Parametern gefunden')
  }
  
  // 2. Prüfe Userbot-Paket-Status (falls User bereits eingeloggt ist)
  await checkUserbotPackageStatus()
  
  // 2. Telegram-ID aus Telegram WebApp Kontext lesen
  if (!telegramId.value && window.Telegram && window.Telegram.WebApp) {
    console.log('🔍 Prüfe Telegram WebApp Kontext...')
    console.log('Telegram WebApp verfügbar:', !!window.Telegram.WebApp)
    console.log('initDataUnsafe:', window.Telegram.WebApp.initDataUnsafe)
    console.log('initData:', window.Telegram.WebApp.initData)
    
    // Prüfe verschiedene WebApp-Datenquellen
    if (window.Telegram.WebApp.initDataUnsafe && window.Telegram.WebApp.initDataUnsafe.user) {
      telegramId.value = window.Telegram.WebApp.initDataUnsafe.user.id.toString()
      console.log('📱 Telegram-ID aus initDataUnsafe.user gelesen:', telegramId.value)
    } else if (window.Telegram.WebApp.initData) {
      // Versuche initData zu parsen
      try {
        const initData = new URLSearchParams(window.Telegram.WebApp.initData)
        const userData = initData.get('user')
        if (userData) {
          const user = JSON.parse(userData)
          telegramId.value = user.id.toString()
          console.log('📱 Telegram-ID aus initData.user gelesen:', telegramId.value)
        }
      } catch (e) {
        console.warn('⚠️ Konnte initData nicht parsen:', e)
      }
    } else {
      console.log('❌ Keine User-Daten im WebApp Kontext gefunden')
    }
  }
  
  // 3. Telegram-ID aus localStorage lesen (falls bereits gespeichert)
  if (!telegramId.value) {
    const storedTelegramId = localStorage.getItem('telegram_id')
    if (storedTelegramId) {
      telegramId.value = storedTelegramId
      console.log('📱 Telegram-ID aus localStorage gelesen:', telegramId.value)
    } else {
      console.log('❌ Keine Telegram-ID im localStorage gefunden')
    }
  }
  
  // 4. Telegram-ID aus Session-Storage lesen
  if (!telegramId.value) {
    const sessionTelegramId = sessionStorage.getItem('telegram_id')
    if (sessionTelegramId) {
      telegramId.value = sessionTelegramId
      console.log('📱 Telegram-ID aus sessionStorage gelesen:', telegramId.value)
    } else {
      console.log('❌ Keine Telegram-ID im sessionStorage gefunden')
    }
  }
  
  // Finale Status-Ausgabe
  if (telegramId.value) {
    console.log('✅ Telegram-ID erfolgreich erkannt:', telegramId.value)
    // Telegram-ID für zukünftige Verwendung speichern
    localStorage.setItem('telegram_id', telegramId.value)
    sessionStorage.setItem('telegram_id', telegramId.value)
  } else {
    console.log('❌ Keine Telegram-ID gefunden - User muss über Bot-Button kommen')
  }
  
  // Auto-Login versuchen, wenn Telegram-ID vorhanden
  if (telegramId.value) {
    try {
      console.log('🔄 Versuche Auto-Login...')
      const result = await authStore.autoLogin(telegramId.value)
      
      if (result.success) {
        console.log('✅ Auto-Login erfolgreich!')
        router.push('/dashboard')
        return
      } else {
        console.warn('❌ Auto-Login fehlgeschlagen:', result.error || 'Unbekannter Fehler')
      }
    } catch (e) {
      console.error('❌ Auto-Login Exception:', e)
    }
  }
  
  // Wenn bereits eingeloggt, zum Dashboard weiterleiten
  if (authStore.isAuthenticated) {
    console.log('✅ Bereits eingeloggt, leite zum Dashboard weiter')
    router.push('/dashboard')
  }
})

const validatePhone = () => {
  phoneError.value = ''
  
  if (!phone.value) {
    return
  }
  
  // Regex für internationale Telefonnummern
  const phoneRegex = /^\+\d{8,20}$/
  
  if (!phoneRegex.test(phone.value)) {
    phoneError.value = 'Bitte geben Sie eine gültige Telefonnummer ein (z.B. +491701234567)'
  }
}

const isPhoneValid = computed(() => {
  if (!phone.value) return false
  const phoneRegex = /^\+\d{8,20}$/
  return phoneRegex.test(phone.value)
})

const linkPhoneToTelegram = async () => {
  if (!isPhoneValid.value) {
    phoneError.value = 'Bitte geben Sie eine gültige Telefonnummer ein'
    return
  }

  if (!telegramId.value) {
    error.value = 'Keine Telegram-ID gefunden. Bitte starten Sie zuerst den Bot.'
    return
  }

  console.log('🚀 Starte Telefonnummer-Verknüpfung für:', phone.value)
  console.log('📱 Telegram-ID:', telegramId.value)
  
  isLoading.value = true
  error.value = ''
  
  try {
    // 1. Telefonnummer mit Telegram-ID verknüpfen
    console.log('🔗 Verknüpfe Telefonnummer mit Telegram-ID...')
    const linkData = await api.linkPhoneToTelegram(telegramId.value, phone.value)
    console.log('✅ Telefonnummer erfolgreich verknüpft:', linkData)

    // 2. Jetzt Code anfordern
    console.log('📨 Fordere Verifizierungscode an...')
    const codeData = await api.requestCode(phone.value, telegramId.value)
    console.log('✅ Code erfolgreich angefordert:', codeData)

    // 3. Zum Code-Eingabe-Schritt wechseln
    codeSent.value = true
    error.value = null

  } catch (err) {
    console.error('❌ Fehler bei der Verknüpfung:', err)
    error.value = 'Verknüpfung fehlgeschlagen: ' + err.message
  } finally {
    isLoading.value = false
  }
}

const requestCode = async () => {
  if (!isPhoneValid.value) {
    phoneError.value = 'Bitte geben Sie eine gültige Telefonnummer ein'
    return
  }

  console.log('🔐 Starte Code-Anfrage für:', phone.value)
  console.log('🔧 Verwende Userbot:', useUserbot.value)
  
  isLoading.value = true
  error.value = ''
  phoneError.value = ''
  
  try {
    let result
    
    if (useUserbot.value && hasUserbotPackage.value) {
      // Versuche zuerst Userbot-Code-Anfrage
      try {
        console.log('👤 Verwende Userbot-Code-Anfrage...')
        const userbotResponse = await userbotAPI.requestCode(phone.value)
        console.log('✅ Userbot-Code-Anfrage:', userbotResponse)
        
        if (userbotResponse.status === 'code_sent') {
          // Userbot-Code-Anfrage erfolgreich
          console.log('✅ Code erfolgreich über Userbot gesendet')
          codeSent.value = true
          return
        } else {
          throw new Error(userbotResponse.message || 'Userbot-Code-Anfrage fehlgeschlagen')
        }
      } catch (userbotError) {
        console.warn('⚠️ Userbot-Code-Anfrage fehlgeschlagen, verwende Backend-Fallback:', userbotError)
        // Fallback: Backend verwenden
        console.log('📡 Verwende Backend-Code-Anfrage...')
        result = await api.requestCode(phone.value, telegramId.value, false)
      }
    } else {
      // Direkt Backend verwenden
      console.log('📡 Verwende Backend-Code-Anfrage...')
      result = await api.requestCode(phone.value, telegramId.value, false)
    }
    
    if (result.success) {
      console.log('✅ Code erfolgreich gesendet')
      codeSent.value = true
    } else {
      error.value = result.error || 'Code-Anfrage fehlgeschlagen'
    }
    
  } catch (err) {
    console.error('❌ Fehler bei der Code-Anfrage:', err)
    console.error('❌ Error Details:', err.response?.data)
    console.error('❌ Error Status:', err.response?.status)
    
    // Bessere Fehlermeldungen
    if (err.message.includes('Network Error')) {
      error.value = 'Verbindungsfehler. Bitte prüfen Sie Ihre Internetverbindung und versuchen Sie es erneut.'
    } else if (err.response?.status === 429) {
      error.value = 'Zu viele Anfragen. Bitte warten Sie einige Minuten und versuchen Sie es erneut.'
    } else if (err.response?.status === 400) {
      error.value = 'Ungültige Telefonnummer. Bitte überprüfen Sie die Nummer und versuchen Sie es erneut.'
    } else {
      error.value = 'Code-Anfrage fehlgeschlagen: ' + err.message
    }
  } finally {
    isLoading.value = false
  }
}

const verifyCode = async () => {
  if (!code.value) {
    error.value = 'Bitte geben Sie den Verifizierungscode ein'
    return
  }

  console.log('🔐 Starte Code-Verifizierung für:', phone.value)
  console.log('🔧 Verwende Userbot:', useUserbot.value)
  
  isLoading.value = true
  error.value = ''
  
  try {
    let result
    
    if (useUserbot.value && hasUserbotPackage.value) {
      // Versuche zuerst Userbot-Verifizierung
      try {
        console.log('👤 Verwende Userbot-Verifizierung...')
        const userbotResponse = await userbotAPI.verifyCode(phone.value, code.value)
        console.log('✅ Userbot-Verifizierung:', userbotResponse)
        
        if (userbotResponse.status === 'success') {
          // Userbot-Verifizierung erfolgreich - jetzt Backend-Login
          console.log('🔄 Userbot erfolgreich, starte Backend-Login...')
          result = await authStore.login(phone.value, code.value)
        } else {
          throw new Error(userbotResponse.message || 'Userbot-Verifizierung fehlgeschlagen')
        }
      } catch (userbotError) {
        console.warn('⚠️ Userbot-Verifizierung fehlgeschlagen, verwende Backend-Fallback:', userbotError)
        // Fallback: Nur Backend verwenden
        console.log('📡 Verwende Backend-Verifizierung...')
        result = await authStore.login(phone.value, code.value)
      }
    } else {
      // Direkt Backend verwenden
      console.log('📡 Verwende Backend-Verifizierung...')
      result = await authStore.login(phone.value, code.value)
    }
    
    if (result.success) {
      console.log('✅ Login erfolgreich')
      router.push('/dashboard')
    } else {
      error.value = result.error || 'Login fehlgeschlagen'
    }
    
  } catch (err) {
    console.error('❌ Fehler bei der Verifizierung:', err)
    console.error('❌ Error Details:', err.response?.data)
    console.error('❌ Error Status:', err.response?.status)
    
    // Bessere Fehlermeldungen
    if (err.message.includes('Network Error')) {
      error.value = 'Verbindungsfehler. Bitte prüfen Sie Ihre Internetverbindung und versuchen Sie es erneut.'
    } else if (err.response?.status === 401) {
      error.value = 'Ungültiger Code. Bitte überprüfen Sie den Code und versuchen Sie es erneut.'
    } else if (err.response?.status === 404) {
      error.value = 'Service nicht verfügbar. Bitte versuchen Sie es später erneut.'
    } else {
      error.value = 'Verifizierung fehlgeschlagen: ' + err.message
    }
  } finally {
    isLoading.value = false
  }
}

const backToPhone = () => {
  codeSent.value = false
  code.value = ''
  error.value = null
}

const testBackendConnection = async () => {
  console.log('🔧 Teste Backend-Verbindung...')
  const API_URL = import.meta.env.VITE_API_URL || 'https://api.bit-team-bot.online'
  
  try {
    const response = await fetch(`${API_URL}/`)
    if (response.ok) {
      const data = await response.json()
      console.log('✅ Backend erreichbar:', data)
      return true
    } else {
      console.error('❌ Backend-Response nicht OK:', response.status)
      return false
    }
  } catch (error) {
    console.error('❌ Backend-Verbindung fehlgeschlagen:', error)
    return false
  }
}
</script>

<style scoped>
/* Header-Styles direkt in der Login-Komponente */
.header-container {
  background: linear-gradient(135deg, var(--bg-primary) 0%, #1a1b22 100%) !important;
  padding: clamp(12px, 2vw, 24px) !important;
  width: 100vw !important;
  max-width: 100vw !important;
  position: relative !important;
  overflow: hidden !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
  min-height: 120px !important;
  height: auto !important;
  max-height: none !important;
  display: flex !important;
  align-items: center !important;
  margin: 0 !important;
  left: 0 !important;
  right: 0 !important;
  flex-shrink: 0 !important;
  flex-grow: 0 !important;
  flex-basis: auto !important;
}

.header-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: url('@/assets/bitcoin-bg.png');
  background-size: cover;
  background-position: center;
  opacity: 0.05;
  z-index: 0;
}

.header-content {
  position: relative;
  z-index: 1;
  width: 100% !important;
  max-width: none !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  margin: 0 !important;
  height: auto !important;
  min-height: 120px !important;
  max-height: none !important;
  flex-shrink: 0 !important;
  flex-grow: 0 !important;
  flex-basis: auto !important;
}

.logo-section {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  transition: all 0.3s ease;
  width: 100% !important;
  max-width: none !important;
  height: auto !important;
  min-height: 120px !important;
  max-height: none !important;
  flex-shrink: 0 !important;
  flex-grow: 0 !important;
  flex-basis: auto !important;
}

.header-logo {
  height: clamp(80px, 15vw, 120px) !important;
  width: auto !important;
  max-width: none !important;
  filter: drop-shadow(0 0 15px rgba(255, 179, 43, 0.6));
  transition: all 0.3s ease;
  object-fit: contain;
  flex-shrink: 0 !important;
  flex-grow: 0 !important;
  flex-basis: auto !important;
}

/* Login-Container Styles */
.login-container {
  min-height: 100vh;
  background-color: var(--bg-primary);
  display: flex;
  flex-direction: column;
  height: auto !important;
  max-height: none !important;
}

.login-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  height: auto !important;
  max-height: none !important;
  min-height: 0 !important;
}

.login-card {
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius);
  padding: 32px;
  width: 100%;
  max-width: 400px;
  box-shadow: var(--shadow-3d);
}

.login-title {
  font-size: 2rem;
  font-weight: bold;
  color: var(--text-white);
  text-align: center;
  margin: 0 0 8px 0;
}

.login-subtitle {
  color: var(--text-gray);
  text-align: center;
  margin: 0 0 32px 0;
  font-size: 1rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-box {
  background-color: rgba(52, 152, 219, 0.1);
  border: 1px solid rgba(52, 152, 219, 0.3);
  border-radius: var(--border-radius);
  padding: 16px;
  color: var(--text-white);
  font-size: 0.9rem;
  text-align: center;
}

.warning-box {
  background: rgba(255, 193, 7, 0.1);
  border: 1px solid rgba(255, 193, 7, 0.3);
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
  color: #856404;
}

.warning-box h4 {
  margin: 0 0 8px 0;
  color: #856404;
}

.warning-box p {
  margin: 0 0 16px 0;
  line-height: 1.5;
}

.solution-steps {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.solution-steps h5 {
  color: #fff;
  margin: 0 0 12px 0;
  font-size: 1rem;
  font-weight: bold;
}

.solution-steps ol {
  margin: 0;
  padding-left: 20px;
  color: #fff;
}

.solution-steps li {
  margin-bottom: 8px;
  line-height: 1.4;
}

.solution-steps .bot-link {
  color: #ffd700;
  text-decoration: none;
  font-weight: bold;
}

.solution-steps .bot-link:hover {
  text-decoration: underline;
}

.solution-steps code {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-weight: bold;
}

.info-box {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 2px solid #0ea5e9;
  border-radius: 12px;
  padding: 20px;
  margin: 15px 0;
  text-align: center;
}

.info-box h4 {
  color: #0369a1;
  margin-bottom: 10px;
  font-size: 16px;
}

.info-box p {
  color: #0c4a6e;
  margin-bottom: 8px;
  font-size: 14px;
  line-height: 1.5;
}

.info-note {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 16px;
  border-left: 4px solid #ffd700;
}

.info-note p {
  color: #fff;
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.info-note p:last-child {
  margin-bottom: 0;
}

.info-note strong {
  color: #ffd700;
}

.bot-link {
  color: #007bff;
  text-decoration: none;
  font-weight: bold;
  background: rgba(0, 123, 255, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.bot-link:hover {
  background: rgba(0, 123, 255, 0.2);
  text-decoration: underline;
}

.warning-box code {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-weight: bold;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-label {
  color: var(--text-white);
  font-weight: 500;
  font-size: 0.9rem;
}

.code-input {
  text-align: center;
  font-size: 1.2rem;
  letter-spacing: 4px;
  font-weight: bold;
}

.code-info {
  color: var(--text-gray);
  font-size: 0.9rem;
  text-align: center;
  margin: 8px 0 0 0;
}

.login-button {
  margin-top: 16px;
}

.test-button {
  margin-top: 12px;
  background-color: var(--accent-orange);
  color: var(--text-white);
  border: none;
  border-radius: var(--border-radius);
  padding: 12px 24px;
  font-weight: bold;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.test-button:hover {
  background-color: #e67e22;
  transform: translateY(-1px);
}

.test-button:disabled {
  background-color: var(--text-gray);
  cursor: not-allowed;
  transform: none;
}

.button-group {
  display: flex;
  gap: 12px;
}

.verify-button {
  flex: 1;
}

.btn-secondary {
  background-color: transparent;
  color: var(--text-gray);
  border: 2px solid var(--text-gray);
  border-radius: var(--border-radius);
  padding: 16px 24px;
  font-weight: bold;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background-color: var(--text-gray);
  color: var(--bg-primary);
}

.language-selector {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--bg-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.language-label {
  color: var(--text-gray);
  font-size: 0.9rem;
}

.language-select {
  background-color: var(--bg-primary);
  color: var(--text-white);
  border: 1px solid var(--text-gray);
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 0.9rem;
}

.language-select:focus {
  outline: none;
  border-color: var(--accent-orange);
}

.debug-link {
  margin-top: 16px;
  text-align: center;
}

.debug-link-text {
  color: var(--text-gray);
  text-decoration: none;
}

/* Responsive Design */
@media (max-width: 768px) {
  .login-content {
    padding: 16px;
  }
  
  .login-card {
    padding: 24px;
  }
  
  .login-title {
    font-size: 1.75rem;
  }
  
  .button-group {
    flex-direction: column;
  }
  
  .header-container {
    min-height: 100px !important;
  }
  
  .header-content {
    min-height: 100px !important;
  }
  
  .logo-section {
    min-height: 100px !important;
  }
}

@media (max-width: 480px) {
  .header-container {
    min-height: 80px !important;
  }
  
  .header-content {
    min-height: 80px !important;
  }
  
  .logo-section {
    min-height: 80px !important;
  }
}

@media (max-width: 320px) {
  .header-container {
    min-height: 60px !important;
  }
  
  .header-content {
    min-height: 60px !important;
  }
  
  .logo-section {
    min-height: 60px !important;
  }
}

/* Landscape-Modus für mobile Geräte */
@media (orientation: landscape) and (max-height: 500px) {
  .header-container {
    min-height: 60px !important;
    padding: clamp(8px, 1.5vw, 16px) !important;
  }
  
  .header-content {
    min-height: 60px !important;
  }
  
  .logo-section {
    min-height: 60px !important;
  }
  
  .header-logo {
    height: clamp(40px, 8vw, 60px) !important;
  }
}

/* Große Bildschirme */
@media (min-width: 1400px) {
  .header-container {
    min-height: 160px !important;
  }
  
  .header-content {
    min-height: 160px !important;
  }
  
  .logo-section {
    min-height: 160px !important;
  }
  
  .header-logo {
    height: clamp(100px, 20vw, 160px) !important;
  }
}

/* Ultra-wide Bildschirme */
@media (min-width: 2000px) {
  .header-container {
    min-height: 200px !important;
  }
  
  .header-content {
    min-height: 200px !important;
  }
  
  .logo-section {
    min-height: 200px !important;
  }
  
  .header-logo {
    height: clamp(120px, 24vw, 200px) !important;
  }
}

/* Hover-Effekte */
.logo-section:hover .header-logo {
  transform: scale(1.05);
  filter: drop-shadow(0 0 20px rgba(255, 179, 43, 0.8));
}

/* Form Styles */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-group input[type="tel"],
.form-group input[type="text"] {
  width: 100%;
  padding: 12px;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-size: 16px;
  transition: border-color 0.3s ease;
}

.form-group input[type="tel"]:focus,
.form-group input[type="text"]:focus {
  outline: none;
  border-color: var(--accent-color);
}

.form-group input.error {
  border-color: var(--error-color);
}

.error-message {
  color: var(--error-color);
  font-size: 14px;
  margin-top: 4px;
  display: block;
}

/* Checkbox Styles */
.checkbox-label {
  display: flex !important;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.checkbox-label input[type="checkbox"] {
  margin-right: 8px;
  width: 16px;
  height: 16px;
  accent-color: var(--accent-color);
}

.help-text {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

/* Success Box */
.success-box {
  background: rgba(40, 167, 69, 0.1);
  border: 1px solid rgba(40, 167, 69, 0.3);
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
  color: #155724;
}

.success-box h4 {
  margin: 0 0 8px 0;
  color: #155724;
}

.success-box code {
  background: rgba(40, 167, 69, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}
</style>
