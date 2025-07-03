<template>
  <div class="debug-container">
      <div class="debug-card">
      <h2>🐛 Debug-Informationen</h2>
        
        <div class="debug-section">
        <h3>📱 Telegram-ID Erkennung</h3>
        <div class="debug-item">
          <strong>URL-Parameter:</strong> 
          <span :class="urlParam ? 'success' : 'error'">
            {{ urlParam || 'Nicht gefunden' }}
          </span>
        </div>
        <div class="debug-item">
          <strong>WebApp Kontext:</strong> 
          <span :class="webAppId ? 'success' : 'error'">
            {{ webAppId || 'Nicht verfügbar' }}
          </span>
          </div>
        <div class="debug-item">
          <strong>localStorage:</strong> 
          <span :class="localStorageId ? 'success' : 'error'">
            {{ localStorageId || 'Nicht gespeichert' }}
          </span>
        </div>
        <div class="debug-item">
          <strong>sessionStorage:</strong> 
          <span :class="sessionStorageId ? 'success' : 'error'">
            {{ sessionStorageId || 'Nicht gespeichert' }}
          </span>
        </div>
        <div class="debug-item">
          <strong>Finale Telegram-ID:</strong> 
          <span :class="finalTelegramId ? 'success' : 'error'">
            {{ finalTelegramId || 'Nicht erkannt' }}
          </span>
          </div>
        </div>

        <div class="debug-section">
        <h3>🌐 Browser-Informationen</h3>
        <div class="debug-item">
          <strong>User Agent:</strong> {{ userAgent }}
        </div>
        <div class="debug-item">
          <strong>URL:</strong> {{ currentUrl }}
        </div>
        <div class="debug-item">
          <strong>Referrer:</strong> {{ referrer }}
          </div>
        </div>

        <div class="debug-section">
        <h3>🔧 Telegram WebApp Status</h3>
        <div class="debug-item">
          <strong>Telegram WebApp verfügbar:</strong> 
          <span :class="telegramWebAppAvailable ? 'success' : 'error'">
            {{ telegramWebAppAvailable ? 'Ja' : 'Nein' }}
          </span>
        </div>
        <div class="debug-item">
          <strong>initDataUnsafe:</strong> 
          <pre class="debug-json">{{ initDataUnsafe }}</pre>
          </div>
        </div>

        <div class="debug-section">
        <h3>🔗 API-Verbindung</h3>
        <div class="debug-item">
          <strong>API URL:</strong> {{ apiUrl }}
        </div>
        <div class="debug-item">
          <strong>Backend Status:</strong> 
          <span :class="backendStatus ? 'success' : 'error'">
            {{ backendStatus ? 'Erreichbar' : 'Nicht erreichbar' }}
          </span>
            </div>
          </div>

      <div class="debug-actions">
        <button @click="refreshDebug" class="btn-primary">🔄 Aktualisieren</button>
        <button @click="clearStorage" class="btn-secondary">🗑️ Storage löschen</button>
        <button @click="testBackend" class="btn-secondary">🔧 Backend testen</button>
      </div>

      <div class="debug-section">
        <h3>📋 Anweisungen</h3>
        <div class="instructions">
          <div class="warning-box">
            <h4>⚠️ Technisches Problem erkannt!</h4>
            <p>Das System wurde so konfiguriert, dass die Telegram-ID nur über Inline-Buttons übertragen wird, nicht über den Menü-Button.</p>
          </div>
          
          <p><strong>So beheben Sie das Problem:</strong></p>
          <ol>
            <li>Öffnen Sie den Telegram-Bot: <a href="https://t.me/bitteam_bot" target="_blank" class="bot-link">@bitteam_bot</a></li>
            <li>Senden Sie <code>/start</code> an den Bot</li>
            <li>Klicken Sie auf den Button "🌐 Webinterface öffnen" (nicht den Menü-Button!)</li>
            <li>Die Telegram-ID wird automatisch übertragen</li>
          </ol>
          
          <div class="info-box">
            <h4>ℹ️ Warum funktioniert das so?</h4>
            <p>Das MenuButtonWebApp von Telegram unterstützt keine dynamischen URLs mit User-Parametern. Daher verwenden wir nur Inline-Buttons, die die Telegram-ID korrekt übertragen können.</p>
          </div>
          
          <div class="success-box">
            <h4>✅ Lösung implementiert!</h4>
            <p>Der Bot wurde so konfiguriert, dass er nur Inline-Buttons verwendet, die die Telegram-ID korrekt übertragen. Der Menü-Button wurde entfernt, um Verwirrung zu vermeiden.</p>
          </div>
          
          <div class="test-box">
            <h4>🧪 Test-Links (nur für Entwicklung):</h4>
            <p>Sie können diese Links testen, um zu sehen, wie die Telegram-ID-Übertragung funktioniert:</p>
            <div class="test-links">
              <a href="?user=123456789" class="test-link">Test mit User 123456789</a>
              <a href="?user=987654321" class="test-link">Test mit User 987654321</a>
              <a href="/debug" class="test-link">Zurück zur Debug-Seite</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const urlParam = ref('')
const webAppId = ref('')
const localStorageId = ref('')
const sessionStorageId = ref('')
const finalTelegramId = ref('')
const userAgent = ref('')
const currentUrl = ref('')
const referrer = ref('')
const telegramWebAppAvailable = ref(false)
const initDataUnsafe = ref('')
const apiUrl = ref('')
const backendStatus = ref(false)

const collectDebugInfo = () => {
  // URL-Parameter
  const urlParams = new URLSearchParams(window.location.search)
  urlParam.value = urlParams.get('user') || ''

  // WebApp Kontext
  if (window.Telegram && window.Telegram.WebApp) {
    telegramWebAppAvailable.value = true
    
    // Versuche WebApp zu initialisieren
    try {
      window.Telegram.WebApp.ready()
      console.log('✅ Telegram WebApp initialisiert')
    } catch (e) {
      console.warn('⚠️ WebApp Initialisierung fehlgeschlagen:', e)
    }
    
    // Prüfe verschiedene Datenquellen
    if (window.Telegram.WebApp.initDataUnsafe && window.Telegram.WebApp.initDataUnsafe.user) {
      webAppId.value = window.Telegram.WebApp.initDataUnsafe.user.id.toString()
    } else if (window.Telegram.WebApp.initData) {
      try {
        const initData = new URLSearchParams(window.Telegram.WebApp.initData)
        const userData = initData.get('user')
        if (userData) {
          const user = JSON.parse(userData)
          webAppId.value = user.id.toString()
        }
      } catch (e) {
        console.warn('⚠️ initData Parsing fehlgeschlagen:', e)
      }
    }
    
    // Sammle alle WebApp-Informationen
    const webAppInfo = {
      initDataUnsafe: window.Telegram.WebApp.initDataUnsafe,
      initData: window.Telegram.WebApp.initData,
      version: window.Telegram.WebApp.version,
      platform: window.Telegram.WebApp.platform,
      colorScheme: window.Telegram.WebApp.colorScheme,
      themeParams: window.Telegram.WebApp.themeParams,
      headerColor: window.Telegram.WebApp.headerColor,
      backgroundColor: window.Telegram.WebApp.backgroundColor,
      isExpanded: window.Telegram.WebApp.isExpanded,
      viewportHeight: window.Telegram.WebApp.viewportHeight,
      viewportStableHeight: window.Telegram.WebApp.viewportStableHeight
    }
    
    initDataUnsafe.value = JSON.stringify(webAppInfo, null, 2)
  }

  // Storage
  localStorageId.value = localStorage.getItem('telegram_id') || ''
  sessionStorageId.value = sessionStorage.getItem('telegram_id') || ''

  // Finale Telegram-ID (wie im Login.vue)
  finalTelegramId.value = urlParam.value || webAppId.value || localStorageId.value || sessionStorageId.value || ''

  // Browser-Informationen
  userAgent.value = navigator.userAgent
  currentUrl.value = window.location.href
  referrer.value = document.referrer || ''

  // API-Informationen
  apiUrl.value = import.meta.env.VITE_API_URL || 'https://api.bit-team-bot.online'
}

const testBackend = async () => {
  try {
    const response = await fetch(`${apiUrl.value}/health`)
    backendStatus.value = response.ok
  } catch (error) {
    backendStatus.value = false
  }
}

const refreshDebug = () => {
  collectDebugInfo()
  testBackend()
}

const clearStorage = () => {
  localStorage.removeItem('telegram_id')
  sessionStorage.removeItem('telegram_id')
  refreshDebug()
}

onMounted(() => {
  collectDebugInfo()
  testBackend()
})
</script>

<style scoped>
.debug-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.debug-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 32px;
  max-width: 800px;
  width: 100%;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.debug-card h2 {
  color: #333;
  margin-bottom: 24px;
  text-align: center;
  font-size: 28px;
}

.debug-section {
  margin-bottom: 32px;
  padding: 20px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 12px;
  border-left: 4px solid #667eea;
}

.debug-section h3 {
  color: #333;
  margin-bottom: 16px;
  font-size: 18px;
}

.debug-item {
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.debug-item strong {
  color: #555;
  min-width: 150px;
}

.success {
  color: #28a745;
  font-weight: bold;
}

.error {
  color: #dc3545;
  font-weight: bold;
}

.debug-json {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
  font-size: 12px;
  overflow-x: auto;
  max-height: 200px;
  overflow-y: auto;
}

.debug-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin: 24px 0;
  flex-wrap: wrap;
}

.btn-primary, .btn-secondary {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-primary:hover, .btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.instructions {
  background: #e3f2fd;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #2196f3;
}

.instructions ol {
  margin: 12px 0;
  padding-left: 20px;
}

.instructions li {
  margin-bottom: 8px;
  line-height: 1.5;
}

.instructions code {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
}

.instructions a {
  color: #2196f3;
  text-decoration: none;
  font-weight: bold;
}

.instructions a:hover {
  text-decoration: underline;
}

.warning-box {
  background: #ffd7d7;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.warning-box h4 {
  color: #dc3545;
  margin-bottom: 8px;
}

.info-box {
  background: #d3d3ff;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.info-box h4 {
  color: #2196f3;
  margin-bottom: 8px;
}

.success-box {
  background: #d3ffd3;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.success-box h4 {
  color: #28a745;
  margin-bottom: 8px;
}

.test-box {
  background: #e3f2fd;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.test-box h4 {
  color: #2196f3;
  margin-bottom: 8px;
}

.test-links {
  display: flex;
  gap: 12px;
}

.test-link {
  background: #2196f3;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  text-decoration: none;
}

.test-link:hover {
  background: #1976d2;
}

@media (max-width: 768px) {
  .debug-container {
    padding: 10px;
  }
  
  .debug-card {
    padding: 20px;
  }
  
  .debug-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .debug-actions {
    flex-direction: column;
  }
}
</style> 