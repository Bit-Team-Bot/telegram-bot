<template>
  <div class="dashboard-container">
    <!-- Header Section -->
    <div class="header-section">
      <img src="@/assets/wallstreet-header.png" alt="Wallstreet Crypto Header" class="header-image" />
    </div>
    <div class="main-content">
      <div class="user-role-box">
        <div class="role-content">
          <div class="role-section" style="flex-direction:column;align-items:center;width:100%;">
            <h2 class="page-title">Telegram Anmeldung</h2>
            <p class="page-subtitle">Melden Sie sich mit Ihrer Telefonnummer an</p>
            <div v-if="error" class="error-box" style="margin-bottom:16px;">{{ error }}</div>
            <div v-if="!codeSent" style="width:100%;max-width:400px;">
              <div class="form-group">
                <label for="phone">Telefonnummer</label>
                <input
                  id="phone"
                  v-model="phone"
                  type="tel"
                  placeholder="+49 123456789"
                  @input="validatePhone"
                  :class="['form-input', { 'error': phoneError }]"
                  :disabled="isLoading"
                  class="w-100"
                />
                <span v-if="phoneError" class="error-message">{{ phoneError }}</span>
              </div>
              <div v-if="telegramId" class="success-box" style="margin-bottom:12px;">
                <h4>✅ Telegram-ID erfasst!</h4>
                <p>Deine Telegram-ID: <code>{{ telegramId }}</code></p>
                <p>Jetzt wird deine Telefonnummer mit deiner Telegram-ID verknüpft.</p>
              </div>
              <div v-if="!telegramId" class="warning-box" style="margin-bottom:12px;">
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
              <button
                @click="linkPhoneToTelegram"
                :disabled="isLoading || !isPhoneValid || !telegramId"
                class="role-btn admin"
                style="width:100%;margin-top:12px;"
              >
                <span v-if="isLoading">Verknüpfe...</span>
                <span v-else>Telefonnummer mit Telegram verknüpfen</span>
              </button>
            </div>
            <div v-else style="width:100%;max-width:400px;">
              <div class="input-group">
                <label for="code" class="input-label">Verifizierungscode</label>
                <input
                  id="code"
                  v-model="code"
                  type="text"
                  placeholder="123456"
                  maxlength="6"
                  required
                  class="form-input code-input"
                  style="width:100%;"
                />
                <p class="code-info">Code wurde an {{ phone }} gesendet</p>
              </div>
              <div class="button-group" style="display:flex;gap:12px;justify-content:center;">
                <button
                  @click="verifyCode"
                  :disabled="isLoading || !code"
                  class="role-btn admin"
                >
                  <span v-if="isLoading">Verifiziere...</span>
                  <span v-else>Code verifizieren</span>
                </button>
                <button
                  @click="backToPhone"
                  :disabled="isLoading"
                  class="role-btn partner"
                >
                  Zurück
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- Sprache & Debug-Link wie gehabt -->
      <div class="language-selector" style="margin-top:32px;text-align:center;">
        <label class="language-label">Sprache</label>
        <select v-model="$i18n.locale" class="language-select">
          <option value="de">Deutsch</option>
          <option value="en">English</option>
        </select>
      </div>
      <div class="debug-link" style="text-align:center;margin-top:12px;">
        <router-link to="/debug" class="debug-link-text">
          🐛 Debug-Informationen
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import { api } from '../api/index.js'

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

onMounted(async () => {
  console.log('Aktuelle URL:', window.location.href)
  const urlParams = new URLSearchParams(window.location.search)
  const userParam = urlParams.get('user')
  const tgidParam = urlParams.get('tgid')
  const telegramIdParam = urlParams.get('telegram_id')
  console.log('URL-Parameter:', { userParam, tgidParam, telegramIdParam })
  if (userParam) {
    telegramId.value = userParam
  } else if (tgidParam) {
    telegramId.value = tgidParam
  } else if (telegramIdParam) {
    telegramId.value = telegramIdParam
  }
  if (!telegramId.value && window.Telegram && window.Telegram.WebApp) {
    if (window.Telegram.WebApp.initDataUnsafe && window.Telegram.WebApp.initDataUnsafe.user) {
      telegramId.value = window.Telegram.WebApp.initDataUnsafe.user.id.toString()
    } else if (window.Telegram.WebApp.initData) {
      try {
        const initData = new URLSearchParams(window.Telegram.WebApp.initData)
        const userData = initData.get('user')
        if (userData) {
          const user = JSON.parse(userData)
          telegramId.value = user.id.toString()
        }
      } catch (e) {}
    }
  }
  if (!telegramId.value) {
    const storedTelegramId = localStorage.getItem('telegram_id')
    if (storedTelegramId) {
      telegramId.value = storedTelegramId
    }
  }
  if (!telegramId.value) {
    const sessionTelegramId = sessionStorage.getItem('telegram_id')
    if (sessionTelegramId) {
      telegramId.value = sessionTelegramId
    }
  }
  if (telegramId.value) {
    localStorage.setItem('telegram_id', telegramId.value)
    sessionStorage.setItem('telegram_id', telegramId.value)
  }
  console.log('Erkannte Telegram-ID:', telegramId.value)

  // Jetzt erst Auto-Login/Redirect versuchen!
  if (telegramId.value) {
    try {
      const result = await authStore.autoLogin(telegramId.value)
      if (result.success) {
        router.push('/dashboard')
        return
      }
    } catch (e) {}
  }
  if (authStore.isAuthenticated) {
    router.push('/dashboard')
  }
})

const validatePhone = () => {
  phoneError.value = ''
  if (!phone.value) return
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
  isLoading.value = true
  error.value = ''
  try {
    await api.linkPhoneToTelegram(telegramId.value, phone.value)
    await api.requestCode(phone.value, telegramId.value)
    codeSent.value = true
    error.value = null
  } catch (err) {
    error.value = 'Verknüpfung fehlgeschlagen: ' + (err.message || err)
  } finally {
    isLoading.value = false
  }
}

const verifyCode = async () => {
  if (!code.value) {
    error.value = 'Bitte geben Sie den Verifizierungscode ein'
    return
  }
  isLoading.value = true
  error.value = ''
  try {
    const result = await api.verifyWebLoginCode(phone.value, code.value)
    if (result.success) {
      // Baue user-Objekt für loginSession
      const userObj = {
        id: result.user.id,
        telegram_id: result.user.telegram_id,
        phone: result.user.phone,
        is_superadmin: result.user.is_superadmin,
        user_name: result.user.user_name || '',
        package_id: result.user.package_id || null,
        role: result.user.role || 'user'
      }
      const sessionData = {
        access_token: result.access_token,
        user: userObj,
        session: result.session || null
      }
      await authStore.loginSession(sessionData)
      router.push('/dashboard')
    } else {
      error.value = result.detail || result.error || 'Login fehlgeschlagen'
    }
  } catch (err) {
    error.value = err.message || 'Verifizierung fehlgeschlagen'
  } finally {
    isLoading.value = false
  }
}

const backToPhone = () => {
  codeSent.value = false
  code.value = ''
  error.value = null
}
</script>

<!-- Styles werden aus globaler index.css verwendet -->
