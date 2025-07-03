<template>
  <div class="test-container">
    <h1>🔍 URL-Parameter Test</h1>
    
    <div class="test-section">
      <h2>URL-Informationen:</h2>
      <p><strong>Aktuelle URL:</strong> {{ currentUrl }}</p>
      <p><strong>User-Parameter:</strong> {{ userParam }}</p>
      <p><strong>Alle Parameter:</strong> {{ allParams }}</p>
    </div>

    <div class="test-section">
      <h2>Telegram-ID Erkennung:</h2>
      <p><strong>Erkannte Telegram-ID:</strong> {{ telegramId }}</p>
      <p><strong>localStorage:</strong> {{ localStorageId }}</p>
      <p><strong>sessionStorage:</strong> {{ sessionStorageId }}</p>
    </div>

    <div class="test-section">
      <h2>Test-Links:</h2>
      <a href="?user=123456789" class="test-link">Test mit User 123456789</a>
      <a href="?user=987654321" class="test-link">Test mit User 987654321</a>
      <a href="/" class="test-link">Ohne Parameter</a>
    </div>

    <div class="test-section">
      <h2>Console-Logs:</h2>
      <div class="console-output">
        <div v-for="(log, index) in logs" :key="index" class="log-entry" :class="log.type">
          <span class="log-time">{{ log.time }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const currentUrl = ref('')
const userParam = ref('')
const allParams = ref('')
const telegramId = ref('')
const localStorageId = ref('')
const sessionStorageId = ref('')
const logs = ref([])

const addLog = (message, type = 'info') => {
  logs.value.push({
    time: new Date().toLocaleTimeString(),
    message,
    type
  })
}

const collectInfo = () => {
  // URL-Informationen
  currentUrl.value = window.location.href
  
  const urlParams = new URLSearchParams(window.location.search)
  userParam.value = urlParams.get('user') || 'Nicht gefunden'
  allParams.value = Object.fromEntries(urlParams.entries())
  
  // Telegram-ID Erkennung (wie im Login.vue)
  const urlParam = urlParams.get('user')
  const webAppId = window.Telegram?.WebApp?.initDataUnsafe?.user?.id?.toString()
  const storedId = localStorage.getItem('telegram_id')
  const sessionId = sessionStorage.getItem('telegram_id')
  
  telegramId.value = urlParam || webAppId || storedId || sessionId || 'Nicht erkannt'
  localStorageId.value = storedId || 'Nicht gespeichert'
  sessionStorageId.value = sessionId || 'Nicht gespeichert'
  
  addLog('URL-Parameter gesammelt', 'info')
  addLog(`User-Parameter: ${userParam.value}`, 'info')
  addLog(`Telegram-ID: ${telegramId.value}`, 'info')
}

onMounted(() => {
  addLog('Test-Seite geladen', 'info')
  collectInfo()
})
</script>

<style scoped>
.test-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.test-section {
  background: #f5f5f5;
  padding: 20px;
  margin: 20px 0;
  border-radius: 8px;
  border-left: 4px solid #007bff;
}

.test-section h2 {
  color: #333;
  margin-top: 0;
}

.test-link {
  display: inline-block;
  margin: 10px;
  padding: 10px 20px;
  background: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 5px;
  transition: background 0.3s;
}

.test-link:hover {
  background: #0056b3;
}

.console-output {
  background: #2c3e50;
  color: #ecf0f1;
  padding: 15px;
  border-radius: 5px;
  max-height: 300px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 14px;
}

.log-entry {
  margin-bottom: 5px;
  padding: 2px 0;
}

.log-entry.info {
  color: #3498db;
}

.log-entry.success {
  color: #27ae60;
}

.log-entry.error {
  color: #e74c3c;
}

.log-time {
  color: #95a5a6;
  margin-right: 10px;
}
</style> 