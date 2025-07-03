<template>
  <div class="userbot-session-manager">
    <div class="session-header">
      <h3>🤖 Userbot Session Manager</h3>
      <div class="session-status" :class="{ 'active': sessionStatus.is_running }">
        <span class="status-indicator"></span>
        {{ sessionStatus.is_running ? 'Aktiv' : 'Inaktiv' }}
      </div>
    </div>

    <div class="session-controls">
      <button 
        @click="startSession" 
        :disabled="isLoading || sessionStatus.is_running"
        class="btn-primary"
      >
        <span v-if="isLoading">Starte...</span>
        <span v-else>Session starten</span>
      </button>
      
      <button 
        @click="stopSession" 
        :disabled="isLoading || !sessionStatus.is_running"
        class="btn-secondary"
      >
        <span v-if="isLoading">Stoppe...</span>
        <span v-else>Session stoppen</span>
      </button>
      
      <button 
        @click="refreshStatus" 
        :disabled="isLoading"
        class="btn-info"
      >
        🔄 Status aktualisieren
      </button>
    </div>

    <div v-if="error" class="error-box">
      {{ error }}
    </div>

    <div v-if="sessionStatus.is_running" class="session-info">
      <h4>Session-Informationen</h4>
      <div class="info-grid">
        <div class="info-item">
          <span class="label">Session Name:</span>
          <span class="value">{{ sessionStatus.session_name }}</span>
        </div>
        <div class="info-item">
          <span class="label">Aktive Verifizierungen:</span>
          <span class="value">{{ sessionStatus.pending_verifications }}</span>
        </div>
      </div>
    </div>

    <div class="session-actions">
      <h4>Session-Aktionen</h4>
      
      <div class="action-group">
        <label for="phone-input">Telefonnummer für Code-Anfrage:</label>
        <input 
          id="phone-input"
          v-model="phoneForCode"
          type="tel"
          placeholder="+49123456789"
          class="input-field"
        />
        <button 
          @click="requestCodeForPhone"
          :disabled="!phoneForCode || isLoading"
          class="btn-primary"
        >
          Code anfordern
        </button>
      </div>

      <div v-if="codeRequested" class="action-group">
        <label for="code-input">Verifizierungscode eingeben:</label>
        <input 
          id="code-input"
          v-model="codeInput"
          type="text"
          placeholder="123456"
          maxlength="6"
          class="input-field"
        />
        <button 
          @click="verifyCodeForPhone"
          :disabled="!codeInput || isLoading"
          class="btn-primary"
        >
          Code verifizieren
        </button>
      </div>
    </div>

    <div class="session-logs">
      <h4>Session-Logs</h4>
      <div class="logs-container">
        <div 
          v-for="(log, index) in sessionLogs" 
          :key="index"
          class="log-entry"
          :class="log.type"
        >
          <span class="log-time">{{ log.time }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { userbotAPI } from '../api/index.js'

const sessionStatus = ref({
  is_running: false,
  session_name: '',
  pending_verifications: 0
})

const isLoading = ref(false)
const error = ref('')
const phoneForCode = ref('')
const codeInput = ref('')
const codeRequested = ref(false)
const sessionLogs = ref([])

let statusInterval = null

onMounted(async () => {
  await refreshStatus()
  // Status alle 30 Sekunden aktualisieren
  statusInterval = setInterval(refreshStatus, 30000)
})

onUnmounted(() => {
  if (statusInterval) {
    clearInterval(statusInterval)
  }
})

const addLog = (message, type = 'info') => {
  const time = new Date().toLocaleTimeString()
  sessionLogs.value.unshift({ time, message, type })
  // Nur die letzten 50 Logs behalten
  if (sessionLogs.value.length > 50) {
    sessionLogs.value = sessionLogs.value.slice(0, 50)
  }
}

const refreshStatus = async () => {
  try {
    const status = await userbotAPI.getSessionStatus()
    sessionStatus.value = status
    addLog('Status aktualisiert', 'info')
  } catch (err) {
    addLog(`Status-Aktualisierung fehlgeschlagen: ${err.message}`, 'error')
  }
}

const startSession = async () => {
  isLoading.value = true
  error.value = ''
  
  try {
    addLog('Starte Userbot-Session...', 'info')
    const result = await userbotAPI.getStatus()
    if (result.is_running) {
      sessionStatus.value = result
      addLog('Userbot-Session bereits aktiv', 'success')
    } else {
      addLog('Userbot-Session gestartet', 'success')
    }
    await refreshStatus()
  } catch (err) {
    error.value = `Fehler beim Starten der Session: ${err.message}`
    addLog(`Session-Start fehlgeschlagen: ${err.message}`, 'error')
  } finally {
    isLoading.value = false
  }
}

const stopSession = async () => {
  isLoading.value = true
  error.value = ''
  
  try {
    addLog('Stoppe Userbot-Session...', 'info')
    await userbotAPI.stopSession()
    addLog('Userbot-Session gestoppt', 'success')
    await refreshStatus()
  } catch (err) {
    error.value = `Fehler beim Stoppen der Session: ${err.message}`
    addLog(`Session-Stop fehlgeschlagen: ${err.message}`, 'error')
  } finally {
    isLoading.value = false
  }
}

const requestCodeForPhone = async () => {
  if (!phoneForCode.value) {
    error.value = 'Bitte geben Sie eine Telefonnummer ein'
    return
  }

  isLoading.value = true
  error.value = ''
  
  try {
    addLog(`Fordere Code für ${phoneForCode.value} an...`, 'info')
    const result = await userbotAPI.requestCode(phoneForCode.value)
    
    if (result.status === 'code_sent') {
      codeRequested.value = true
      addLog(`Code erfolgreich an ${phoneForCode.value} gesendet`, 'success')
    } else {
      throw new Error(result.message || 'Code-Anfrage fehlgeschlagen')
    }
  } catch (err) {
    error.value = `Fehler bei Code-Anfrage: ${err.message}`
    addLog(`Code-Anfrage fehlgeschlagen: ${err.message}`, 'error')
  } finally {
    isLoading.value = false
  }
}

const verifyCodeForPhone = async () => {
  if (!codeInput.value) {
    error.value = 'Bitte geben Sie den Code ein'
    return
  }

  isLoading.value = true
  error.value = ''
  
  try {
    addLog(`Verifiziere Code für ${phoneForCode.value}...`, 'info')
    const result = await userbotAPI.verifyCode(phoneForCode.value, codeInput.value)
    
    if (result.status === 'success') {
      addLog(`Code erfolgreich für ${phoneForCode.value} verifiziert`, 'success')
      codeRequested.value = false
      codeInput.value = ''
      phoneForCode.value = ''
    } else {
      throw new Error(result.message || 'Code-Verifizierung fehlgeschlagen')
    }
  } catch (err) {
    error.value = `Fehler bei Code-Verifizierung: ${err.message}`
    addLog(`Code-Verifizierung fehlgeschlagen: ${err.message}`, 'error')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.userbot-session-manager {
  background: var(--bg-secondary);
  border-radius: var(--border-radius);
  padding: 24px;
  margin: 16px 0;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.session-header h3 {
  margin: 0;
  color: var(--text-white);
}

.session-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  background: rgba(220, 53, 69, 0.2);
  color: #dc3545;
}

.session-status.active {
  background: rgba(40, 167, 69, 0.2);
  color: #28a745;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.session-controls {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.btn-primary, .btn-secondary, .btn-info {
  padding: 8px 16px;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-secondary {
  background: var(--secondary-color);
  color: white;
}

.btn-info {
  background: var(--info-color);
  color: white;
}

.btn-primary:disabled, .btn-secondary:disabled, .btn-info:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-box {
  background: rgba(220, 53, 69, 0.1);
  border: 1px solid rgba(220, 53, 69, 0.3);
  border-radius: var(--border-radius);
  padding: 12px;
  margin: 16px 0;
  color: #dc3545;
}

.session-info {
  background: rgba(52, 152, 219, 0.1);
  border: 1px solid rgba(52, 152, 219, 0.3);
  border-radius: var(--border-radius);
  padding: 16px;
  margin: 16px 0;
}

.session-info h4 {
  margin: 0 0 12px 0;
  color: var(--text-white);
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
}

.label {
  color: var(--text-gray);
  font-weight: 500;
}

.value {
  color: var(--text-white);
  font-weight: bold;
}

.session-actions {
  margin: 20px 0;
}

.session-actions h4 {
  margin: 0 0 16px 0;
  color: var(--text-white);
}

.action-group {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.action-group label {
  color: var(--text-white);
  font-weight: 500;
  min-width: 200px;
}

.input-field {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--bg-primary);
  color: var(--text-white);
  font-size: 14px;
  min-width: 150px;
}

.session-logs {
  margin-top: 20px;
}

.session-logs h4 {
  margin: 0 0 12px 0;
  color: var(--text-white);
}

.logs-container {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.log-entry {
  display: flex;
  gap: 12px;
  padding: 4px 0;
  font-size: 12px;
  font-family: 'Courier New', monospace;
}

.log-entry.info {
  color: var(--text-gray);
}

.log-entry.success {
  color: #28a745;
}

.log-entry.error {
  color: #dc3545;
}

.log-time {
  color: var(--text-gray);
  min-width: 80px;
}

.log-message {
  flex: 1;
}

@media (max-width: 768px) {
  .session-controls {
    flex-direction: column;
  }
  
  .action-group {
    flex-direction: column;
    align-items: stretch;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style> 