<template>
  <div class="dashboard-container">
    <!-- Header Section -->
    <div class="header-section">
      <img src="@/assets/wallstreet-header.png" alt="Wallstreet Crypto Header" class="header-image" />
    </div>
    
    <!-- Main Content -->
    <div class="main-content">
      <div class="groups-container">
        <main class="groups-content">
          <div class="page-header">
            <h1 class="page-title">Gruppen</h1>
            <p class="page-subtitle">Verwalten Sie Ihre Telegram-Gruppen und Nachrichtenweiterleitung</p>
          </div>

          <!-- Nachrichtenweiterleitung User Role Box -->
          <div class="user-role-box">
            <div class="role-content">
              <div class="section-header">
                <h2>Nachrichtenweiterleitung</h2>
                <p>Leiten Sie Nachrichten automatisch zwischen Ihren Telegram-Gruppen weiter</p>
              </div>
              
              <!-- Kein Paket Nachricht für normale User -->
              <div v-if="showNoPackageMessage" class="no-package-message">
                <div class="message-content">
                  <div class="message-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                  </div>
                  <div class="message-text">
                    <h3>Paket erforderlich</h3>
                    <p>Für die Nachrichtenweiterleitung benötigen Sie ein aktives Paket.</p>
                    <button @click="$router.push('/packages')" class="role-btn admin">
                      Pakete anzeigen
                    </button>
                  </div>
                </div>
              </div>

              <!-- Userbot Session Status -->
              <div v-else-if="!userbotSession" class="userbot-login-section">
                <div class="login-card">
                  <h3>Userbot-Session erforderlich</h3>
                  <p>Um Nachrichtenweiterleitung zu nutzen, müssen Sie sich mit Ihrem Telegram-Account anmelden.</p>
                  
                  <!-- Telefonnummer Eingabe -->
                  <div v-if="!showCodeInput" class="phone-input-section">
                    <div class="input-group">
                      <label>Telefonnummer (mit Ländervorwahl):</label>
                      <input 
                        v-model="phoneNumber" 
                        type="tel" 
                        placeholder="+49123456789"
                        class="form-input"
                      />
                    </div>
                    <button @click="requestCode()" class="role-btn admin" :disabled="!phoneNumber">
                      Code anfordern
                    </button>
                  </div>

                  <!-- Code Eingabe -->
                  <div v-if="showCodeInput" class="code-input-section">
                    <div class="input-group">
                      <label>Telegram-Code:</label>
                      <input 
                        v-model="verificationCode" 
                        type="text" 
                        placeholder="12345"
                        class="form-input"
                        maxlength="5"
                      />
                    </div>
                    <div class="button-group">
                      <button @click="verifyCode" class="role-btn admin" :disabled="!verificationCode">
                        Verifizieren
                      </button>
                      <button @click="resetLogin" class="role-btn partner">
                        Zurück
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Weiterleitungsverwaltung -->
              <div v-else class="forwarding-management">
                <div class="forwarding-status">
                  <h4>Userbot-Session aktiv</h4>
                  <p>Sie können jetzt Nachrichtenweiterleitungen einrichten.</p>
                </div>
                <button @click="disconnectSession" class="role-btn logout-btn mt-12">
                  Session trennen
                </button>
                <!-- Neue Weiterleitung erstellen -->
                <div class="new-forwarding-section">
                  <h4>Neue Weiterleitung erstellen</h4>
                  <div class="forwarding-form">
                    <div class="form-row">
                      <div class="input-group">
                        <label>Quellgruppe:</label>
                        <select v-model="newForwarding.sourceGroup" class="form-input dropdown-dark-fix">
                          <option value="">Quellgruppe auswählen</option>
                          <option v-for="group in availableGroups" :key="group.id" :value="group.id">
                            {{ group.name }}
                          </option>
                        </select>
                      </div>
                      <div class="input-group">
                        <label>Zielgruppe:</label>
                        <select v-model="newForwarding.targetGroup" class="form-input dropdown-dark-fix">
                          <option value="">Zielgruppe auswählen</option>
                          <option v-for="group in availableGroups" :key="group.id" :value="group.id">
                            {{ group.name }}
                          </option>
                        </select>
                      </div>
                    </div>
                    <button @click="createForwarding" class="role-btn admin" 
                            :disabled="!newForwarding.sourceGroup || !newForwarding.targetGroup">
                      Weiterleitung erstellen
                    </button>
                  </div>
                </div>

                <!-- Aktive Weiterleitungen -->
                <div class="active-forwardings-section">
                  <h4>Aktive Weiterleitungen</h4>
                  <div v-if="forwardings.length === 0" class="no-forwardings">
                    <p>Keine aktiven Weiterleitungen vorhanden.</p>
                  </div>
                  <div v-else class="forwardings-list">
                    <div v-for="forwarding in forwardings" :key="forwarding.id" class="forwarding-item">
                      <div class="forwarding-info">
                        <div class="forwarding-arrow">
                          <span class="source-group">{{ getGroupName(forwarding.source_group_id) }}</span>
                          <span class="arrow">→</span>
                          <span class="target-group">{{ getGroupName(forwarding.target_group_id) }}</span>
                        </div>
                        <div class="forwarding-status">
                          <span :class="['status-badge', forwarding.forwarding_active ? 'status-active' : 'status-inactive']">
                            {{ forwarding.forwarding_active ? 'Aktiv' : 'Inaktiv' }}
                          </span>
                        </div>
                      </div>
                      <div class="forwarding-actions">
                        <button @click="toggleForwarding(forwarding)" class="role-btn partner">
                          {{ forwarding.forwarding_active ? 'Deaktivieren' : 'Aktivieren' }}
                        </button>
                        <button @click="deleteForwarding(forwarding)" class="logout-btn">
                          Löschen
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- NEUE USER-ROLE-BOX: Signalgruppen-Verwaltung -->
                <div class="user-role-box mt-32">
                  <div class="role-content">
                    <div class="section-header">
                      <h2>Signalgruppen</h2>
                      <p>Wählen Sie Ihre Signalgruppen entsprechend Ihres gebuchten Pakets aus.</p>
                    </div>
                    <div v-if="signalGroups.length === 0" class="no-groups">
                      <p>Keine Signalgruppen verfügbar.</p>
                    </div>
                    <div v-else class="signal-groups-grid">
                      <div v-for="group in signalGroups" :key="group.id" class="signal-group-card" :class="{ 'selected': selectedGroups.includes(group.id) }">
                        <div class="group-header">
                          <h3>{{ group.name }}</h3>
                          <p class="description">{{ group.description }}</p>
                        </div>
                        <div class="group-actions">
                          <label>Anzahl Gruppen:</label>
                          <select v-model="groupSelections[group.id]" @change="updateSelection(group.id)" class="dropdown-dark-fix">
                            <option value="0">Nicht ausgewählt</option>
                            <option v-for="n in maxSignalGroups" :key="n" :value="n">{{ n }} Gruppe{{ n > 1 ? 'n' : '' }}</option>
                          </select>
                          <div v-if="groupSelections[group.id] > 0" class="selected-price">
                            <span>Preis: €{{ getSelectedPrice(group) }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div v-if="totalPrice > 0" class="summary-section">
                      <div class="summary-card">
                        <h3>Zusammenfassung</h3>
                        <div class="summary-items">
                          <div v-for="group in selectedGroupsData" :key="group.id" class="summary-item">
                            <span class="item-name">{{ group.name }} ({{ groupSelections[group.id] }} Gruppen)</span>
                            <span class="item-price">€{{ getSelectedPrice(group) }}</span>
                          </div>
                        </div>
                        <div class="summary-total">
                          <span class="total-label">Gesamtpreis pro Monat:</span>
                          <span class="total-price">€{{ totalPrice }}</span>
                        </div>
                        <button @click="purchaseSignalGroups" class="btn-purchase">
                          Signalgruppen kaufen
                        </button>
                      </div>
                    </div>
                    <div v-else class="no-selection">
                      <p>Wählen Sie mindestens eine Signalgruppe aus, um fortzufahren.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="back-section mt-32">
            <button @click="$router.push('/dashboard')" class="btn-secondary">
              ← Zurück zum Dashboard
            </button>
          </div>
        </main>
      </div>
    </div>
    <!-- Signalgruppen-Box nur anzeigen, wenn hasSignalGroupFeature -->
    <div v-if="hasSignalGroupFeature && signalGroups.length > 0" class="user-role-box mt-32">
      <div class="role-content">
        <div class="section-header">
          <h2>Signalgruppen</h2>
          <p>Wählen Sie Ihre Signalgruppen entsprechend Ihres gebuchten Pakets aus.</p>
        </div>
        <div v-if="signalGroups.length === 0" class="no-groups">
          <p>Keine Signalgruppen verfügbar.</p>
        </div>
        <div v-else class="signal-groups-grid">
          <div v-for="group in signalGroups" :key="group.id" class="signal-group-card" :class="{ 'selected': selectedGroups.includes(group.id) }">
            <div class="group-header">
              <h3>{{ group.name }}</h3>
              <p class="description">{{ group.description }}</p>
            </div>
            <div class="group-actions">
              <label>Anzahl Gruppen:</label>
              <select v-model="groupSelections[group.id]" @change="updateSelection(group.id)" class="dropdown-dark-fix">
                <option value="0">Nicht ausgewählt</option>
                <option v-for="n in maxSignalGroups" :key="n" :value="n">{{ n }} Gruppe{{ n > 1 ? 'n' : '' }}</option>
              </select>
              <div v-if="groupSelections[group.id] > 0" class="selected-price">
                <span>Preis: €{{ getSelectedPrice(group) }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-if="totalPrice > 0" class="summary-section">
          <div class="summary-card">
            <h3>Zusammenfassung</h3>
            <div class="summary-items">
              <div v-for="group in selectedGroupsData" :key="group.id" class="summary-item">
                <span class="item-name">{{ group.name }} ({{ groupSelections[group.id] }} Gruppen)</span>
                <span class="item-price">€{{ getSelectedPrice(group) }}</span>
              </div>
            </div>
            <div class="summary-total">
              <span class="total-label">Gesamtpreis pro Monat:</span>
              <span class="total-price">€{{ totalPrice }}</span>
            </div>
            <button @click="purchaseSignalGroups" class="btn-purchase">
              Signalgruppen kaufen
            </button>
          </div>
        </div>
        <div v-else class="no-selection">
          <p>Wählen Sie mindestens eine Signalgruppe aus, um fortzufahren.</p>
        </div>
      </div>
    </div>
    <div v-if="mappingError" class="debug-box" style="color:#ff6b6b;">Fehler: {{ mappingError }}</div>
    <div class="debug-box" style="background:#222;color:#fff;max-width:100vw;overflow:auto;font-size:12px;">
      <b>Debug:</b>
      <pre>{{ debugVars }}</pre>
      <b>Letzte API-Response:</b>
      <pre>{{ lastApiResponse }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useToast } from 'vue-toastification'
import axios from 'axios'
import { userbotAPI, api } from '../api/index.js'

const authStore = useAuthStore()
const toast = useToast()

// Reaktive Daten für Nachrichtenweiterleitung
const userbotSession = ref(null)
const phoneNumber = ref('')
const verificationCode = ref('')
const showCodeInput = ref(false)
const availableGroups = ref([])
const forwardings = ref([])
const newForwarding = ref({
  sourceGroup: '',
  targetGroup: ''
})
const debugInfo = ref('')
let loadGroupsCalled = false

// Computed Properties
const showNoPackageMessage = computed(() => {
  return !authStore.isSuperadmin && 
         !authStore.isPartner && 
         !authStore.user?.package_id
})

const hasSignalGroupFeature = computed(() => {
  const user = authStore.user
  if (!user || !user.package_id) return false
  // Prüfe auf bekannte Signalgruppen-Feature-Keys
  const features = user.features || {}
  return features.signal_groups_basic || features.signal_groups_pro || features.signal_groups_expert
})

// Methods für Nachrichtenweiterleitung
const requestCode = async () => {
  debugVars.value = {
    phoneNumber: phoneNumber.value,
    userbotSession: userbotSession.value,
    userbotSessionId: userbotSessionId.value,
    availableGroups: availableGroups.value,
    forwardings: forwardings.value,
    event: 'requestCode-force-direct'
  }
  console.log('DEBUG: phoneNumber vor Code-Anforderung:', phoneNumber.value)
  toast.info('Button wurde geklickt - requestCode startet')
  try {
    // 1. Session anlegen
    const sessionResult = await userbotAPI.userbotCreateSession(phoneNumber.value)
    console.log('API Antwort createSession:', sessionResult)
    toast.info('API Antwort createSession: ' + JSON.stringify(sessionResult))
    
    if (sessionResult.success) {
      // 2. Code anfordern
      const codeResult = await userbotAPI.userbotSendCode(phoneNumber.value)
      console.log('API Antwort sendCode:', codeResult)
      toast.info('API Antwort sendCode: ' + JSON.stringify(codeResult))
      
      if (codeResult.success) {
        showCodeInput.value = true
        toast.success('Verifizierungscode wurde gesendet')
      } else {
        toast.error(codeResult.error || 'Code-Versand fehlgeschlagen')
      }
    } else {
      toast.error(sessionResult.error || 'Session-Erstellung fehlgeschlagen')
    }
  } catch (error) {
    console.error('Fehler bei der Code-Anfrage:', error)
    toast.error('Fehler bei der Code-Anfrage: ' + error.message)
  }
}

const verifyCode = async () => {
  mappingError.value = '' // Fehler zurücksetzen
  try {
    console.log('🔧 Userbot: Verifiziere Code für:', phoneNumber.value)
    const result = await userbotAPI.verifyCode(phoneNumber.value, verificationCode.value)
    
    if (result.success || result.status === 'success') {
      mappingError.value = '' // Fehler nach Erfolg zurücksetzen
      console.log('✅ Userbot: Code erfolgreich verifiziert:', result)
      await createUserbotSession()
      toast.success("Userbot-Session erfolgreich erstellt")
      // Session im Backend speichern
      try {
        await api.saveUserbotSession({
          phone: phoneNumber.value,
          session_name: "Nachrichtenweiterleitung",
          session_type: "message_forwarding",
          telegram_session_string: result.session_string || result.telegram_session_string || '',
          is_active: true
        })
        toast.success("Session im Backend gespeichert")
      } catch (err) {
        toast.error("Fehler beim Speichern im Backend: " + (err.message || err))
      }
      await loadGroups()
      await loadForwardings()
      userbotSession.value = {
        id: 'userbot-session',
        session_name: "Nachrichtenweiterleitung",
        session_type: "message_forwarding",
        phone: phoneNumber.value,
        is_active: true,
        forwarding_enabled: true
      }
      localStorage.setItem('userbot_session', JSON.stringify(userbotSession.value))
      // NEU: Nach erfolgreicher Verifizierung SessionId laden
      await loadExistingSession()
      showCodeInput.value = false // <--- HIER hinzugefügt
      // Sofortige Debug-Ausgabe der Sessions
      try {
        const mySessionsResult = await userbotAPI.getMySessions()
        updateDebugVars({ mySessionsResult })
      } catch (e) {}
    } else {
      toast.error(result.error || result.message || "Ungültiger Code")
    }
  } catch (error) {
    console.error("Fehler bei der Code-Verifikation:", error)
    toast.error("Fehler bei der Code-Verifikation: " + error.message)
  }
}

const createUserbotSession = async () => {
  try {
    console.log('🔧 Userbot: Prüfe Session-Status für:', phoneNumber.value)
    const result = await userbotAPI.getSessionStatus(phoneNumber.value)
    
    if (result.success && result.is_active) {
      userbotSession.value = {
        id: 'userbot-session',
        session_name: "Nachrichtenweiterleitung",
        session_type: "message_forwarding",
        phone: phoneNumber.value,
        is_active: true,
        forwarding_enabled: true
      }
      // NEU: Nach erfolgreicher Session-Erstellung SessionId laden
      await loadExistingSession()
    }
  } catch (error) {
    console.error("Fehler beim Erstellen der Userbot-Session:", error)
    await loadExistingSession()
  }
}

const loadExistingSession = async () => {
  try {
    console.log('🔧 Userbot: Hole eigene Userbot-Sessions')
    const mySessionsResult = await userbotAPI.getMySessions()
    console.log('Userbot-Sessions Response:', mySessionsResult)
    updateDebugVars({ mySessionsResult }) // <--- Debug-Ausgabe ergänzen
    if (mySessionsResult.success && mySessionsResult.sessions && mySessionsResult.sessions.length > 0) {
      // Finde die erste aktive Session
      const activeSession = mySessionsResult.sessions.find(session => session.is_active)
      if (activeSession) {
        userbotSession.value = {
          id: 'userbot-session',
          session_name: activeSession.session_name,
          session_type: activeSession.session_type,
          phone: activeSession.phone,
          is_active: true,
          forwarding_enabled: true
        }
        userbotSessionId.value = activeSession.id
        phoneNumber.value = activeSession.phone
        await loadGroups()
        await loadForwardings()
        return
      } else {
        userbotSession.value = null
        userbotSessionId.value = null
        toast.info('Keine aktive Userbot-Session gefunden. Bitte erneut anmelden.')
      }
    } else {
      userbotSession.value = null
      userbotSessionId.value = null
      toast.info('Keine Userbot-Session gefunden. Bitte anmelden.')
    }
  } catch (error) {
    console.error('Fehler beim Laden eigener Userbot-Sessions:', error)
    userbotSession.value = null
    userbotSessionId.value = null
    toast.error('Fehler beim Laden der Userbot-Sessions')
  }
}

const resetLogin = () => {
  showCodeInput.value = false
  verificationCode.value = ''
  phoneNumber.value = ''
}

// Debug-Infos für das UI
const debugVars = ref({})
const lastApiResponse = ref(null)

const updateDebugVars = (extra = {}) => {
  // mySessionsResult persistent halten
  const oldMySessionsResult = debugVars.value.mySessionsResult
  debugVars.value = {
    phoneNumber: phoneNumber.value,
    userbotSession: userbotSession.value,
    userbotSessionId: userbotSessionId.value,
    availableGroups: availableGroups.value,
    forwardings: forwardings.value,
    ...extra
  }
  if (oldMySessionsResult && !debugVars.value.mySessionsResult) {
    debugVars.value.mySessionsResult = oldMySessionsResult
  }
}

const loadGroups = async () => {
  loadGroupsCalled = true
  try {
    updateDebugVars({ event: 'loadGroups start' })
    if (!phoneNumber.value) {
      debugInfo.value = `loadGroups wurde aufgerufen, aber phoneNumber ist leer!\nUserbot-Session: ${JSON.stringify(userbotSession.value)}\nPaketdaten: ${JSON.stringify(authStore.user)}`
      updateDebugVars({ error: 'phoneNumber leer' })
      return
    }
    const result = await userbotAPI.getChats(phoneNumber.value)
    lastApiResponse.value = result
    debugInfo.value = `loadGroups wurde aufgerufen\nphoneNumber: ${phoneNumber.value}\nAPI-Response: ${JSON.stringify(result, null, 2)}\nUserbot-Session: ${JSON.stringify(userbotSession.value)}\nPaketdaten: ${JSON.stringify(authStore.user)}`
    updateDebugVars({ result })
    if (result.success) {
      availableGroups.value = result.chats || []
    } else {
      toast.error(result.error || "Fehler beim Laden der Gruppen")
    }
  } catch (error) {
    debugInfo.value = `Fehler: ${error.message}\nUserbot-Session: ${JSON.stringify(userbotSession.value)}\nPaketdaten: ${JSON.stringify(authStore.user)}`
    updateDebugVars({ error })
    toast.error("Fehler beim Laden der Gruppen: " + error.message)
  }
}

const loadForwardings = async () => {
  try {
    // Verwende die externe Userbot API für Status
    const response = await axios.get("https://userbot.bit-team-bot.online/status", {
      timeout: 10000,
      headers: { 'Content-Type': 'application/json' }
    })
    console.log('Userbot Status Response:', response.data)
    if (response.data.is_running) {
      userbotSession.value = {
        id: 'userbot-session',
        session_name: "Nachrichtenweiterleitung",
        session_type: "message_forwarding",
        phone: phoneNumber.value,
        is_active: true,
        forwarding_enabled: true
      }
      forwardings.value = response.data.forwardings || []
    }
  } catch (error) {
    console.error("Fehler beim Laden der Weiterleitungen:", error)
    console.error("Error Response:", error.response?.data)
  }
}

const createForwarding = async () => {
  mappingError.value = '' // Fehler zurücksetzen
  updateDebugVars({ event: 'createForwarding start', newForwarding: newForwarding.value })
  try {
    const sourceGroupObj = availableGroups.value.find(g => g.id === newForwarding.value.sourceGroup)
    const targetGroupObj = availableGroups.value.find(g => g.id === newForwarding.value.targetGroup)
    if (!sourceGroupObj || !targetGroupObj) {
      toast.error('Bitte Quell- und Zielgruppe korrekt auswählen.')
      updateDebugVars({ error: 'Quell- oder Zielgruppe fehlt' })
      return
    }
    selectedSourceGroup.value = sourceGroupObj
    selectedTargetGroup.value = targetGroupObj
    const mappingResult = await createMapping()
    lastApiResponse.value = mappingResult
    updateDebugVars({ mappingResult })
    // mappingResult kann Response oder Fehlertext sein
    if (mappingResult && mappingResult.status === 'success') {
      mappingError.value = '' // Fehler nach Erfolg zurücksetzen
      toast.success('Weiterleitung wurde erstellt!')
      console.log('API-Response:', mappingResult)
      newForwarding.value.sourceGroup = ''
      newForwarding.value.targetGroup = ''
    } else {
      toast.error('Fehler beim Erstellen der Weiterleitung: ' + (mappingResult?.message || mappingError.value))
      console.error('API-Fehler:', mappingResult)
    }
  } catch (error) {
    updateDebugVars({ error })
    toast.error('Fehler beim Erstellen der Weiterleitung: ' + (error.message || error))
    console.error('Fehler beim Erstellen der Weiterleitung:', error)
  }
}

const toggleForwarding = async (forwarding) => {
  try {
    // TODO: Weiterleitungs-API im lokalen Service implementieren
    toast.info("Weiterleitungs-Funktion wird noch implementiert")
    console.log('Weiterleitung umschalten:', forwarding)
  } catch (error) {
    console.error("Fehler beim Umschalten der Weiterleitung:", error)
    toast.error("Fehler beim Umschalten der Weiterleitung")
  }
}

const deleteForwarding = async (forwarding) => {
  if (!confirm("Möchten Sie diese Weiterleitung wirklich löschen?")) {
    return
  }
  
  try {
    // TODO: Weiterleitungs-API im lokalen Service implementieren
    toast.info("Weiterleitungs-Funktion wird noch implementiert")
    console.log('Weiterleitung löschen:', forwarding)
  } catch (error) {
    console.error("Fehler beim Löschen der Weiterleitung:", error)
    toast.error("Fehler beim Löschen der Weiterleitung")
  }
}

const getGroupName = (groupId) => {
  const group = availableGroups.value.find(g => g.id === groupId)
  return group ? group.name : `Gruppe ${groupId}`
}

// NEUE USER-ROLE-BOX: Signalgruppen-Verwaltung
const signalGroups = ref([])
const selectedGroups = ref([])
const groupSelections = ref({})
const maxSignalGroups = ref(1)

const selectedGroupsData = computed(() => {
  return signalGroups.value.filter(group => selectedGroups.value.includes(group.id))
})
const totalPrice = computed(() => {
  return selectedGroupsData.value.reduce((total, group) => {
    return total + getSelectedPrice(group)
  }, 0)
})

const loadSignalGroups = async () => {
  try {
    const response = await axios.get('/admin/signal-groups')
    signalGroups.value = response.data.filter(group => group.is_active)
    // Initialisiere Auswahl
    signalGroups.value.forEach(group => {
      groupSelections.value[group.id] = 0
    })
  } catch (error) {
    console.error('Fehler beim Laden der Signalgruppen:', error)
    toast.error('Fehler beim Laden der Signalgruppen')
  }
}
const updateSelection = (groupId) => {
  const selection = groupSelections.value[groupId]
  if (selection > 0) {
    if (!selectedGroups.value.includes(groupId)) {
      selectedGroups.value.push(groupId)
    }
  } else {
    selectedGroups.value = selectedGroups.value.filter(id => id !== groupId)
  }
}
const getSelectedPrice = (group) => {
  const selection = groupSelections.value[group.id]
  switch (selection) {
    case 1: return group.price_1_group
    case 2: return group.price_2_groups
    case 3: return group.price_3_groups
    case 4: return group.price_4_groups
    case 5: return group.price_5_groups
    default: return 0
  }
}
const purchaseSignalGroups = async () => {
  try {
    const purchaseData = {
      signal_groups: selectedGroupsData.value.map(group => ({
        id: group.id,
        name: group.name,
        group_count: groupSelections.value[group.id],
        price: getSelectedPrice(group)
      })),
      total_price: totalPrice.value
    }
    // Weiterleitung zur Zahlungsseite
    window.location.href = `/payments?type=signal_groups&data=${encodeURIComponent(JSON.stringify(purchaseData))}`
    toast.success('Weiterleitung zur Zahlungsseite...')
  } catch (error) {
    console.error('Fehler beim Kauf der Signalgruppen:', error)
    toast.error('Fehler beim Kauf der Signalgruppen')
  }
}

// Methoden
const resetSessionState = () => {
  userbotSession.value = null
  phoneNumber.value = ''
  verificationCode.value = ''
  showCodeInput.value = false
  availableGroups.value = []
  forwardings.value = []
  userbotSessionId.value = null
  localStorage.removeItem('userbot_session')
}

const disconnectSession = async () => {
  updateDebugVars({ event: 'disconnectSession start' })
  let phone = phoneNumber.value
  if (!phone && userbotSession.value && userbotSession.value.phone) {
    phone = userbotSession.value.phone
    updateDebugVars({ info: 'Fallback: phone aus userbotSession genommen', phone })
  }
  if (!phone) {
    // Kein Logout-API-Call möglich, aber trotzdem State zurücksetzen
    resetSessionState()
    updateDebugVars({ error: 'phoneNumber leer, harter Reset' })
    return
  }
  try {
    const response = await userbotAPI.disconnectSession(phone)
    lastApiResponse.value = response
    updateDebugVars({ response })
    resetSessionState()
    toast.success("Userbot-Session wurde getrennt.")
  } catch (error) {
    updateDebugVars({ error })
    // NEU: Auch bei Fehler den State zurücksetzen!
    resetSessionState()
    toast.error("Fehler beim Trennen der Session: " + (error.message || error))
  }
}

// --- Quell- und Zielgruppen-Auswahl, Mapping-Logik und API-Calls integriert ---
// 1. Neue States für Mapping-Logik
const userbotSessionId = ref(null)
const selectedSourceGroup = ref(null)
const selectedTargetGroup = ref(null)
const existingMappings = ref([])
const mappingError = ref('')

// 2. Session-ID setzen nach erfolgreicher Verifizierung/Session-Status
const setUserbotSessionId = async () => {
  try {
    const mySessionsResult = await userbotAPI.getMySessions()
    if (mySessionsResult.success && mySessionsResult.sessions && mySessionsResult.sessions.length > 0) {
      const activeSession = mySessionsResult.sessions.find(session => session.is_active)
      if (activeSession) {
        userbotSessionId.value = activeSession.id
      }
    }
  } catch (e) {
    mappingError.value = 'Fehler beim Laden der Session-ID'
  }
}

// 3. Gruppen (Dialogs) laden
const loadDialogs = async () => {
  if (!userbotSessionId.value) return
  try {
    const response = await api.get(`/groups/dialogs`)
    if (response.data.status === 'success') {
      availableGroups.value = response.data.dialogs
    } else {
      mappingError.value = 'Fehler beim Laden der Gruppen'
    }
  } catch (err) {
    mappingError.value = 'Fehler beim Laden der Gruppen: ' + (err.message || err)
  }
}

// 4. Mappings laden
const loadExistingMappings = async () => {
  if (!userbotSessionId.value) return
  try {
    const response = await api.get(`/groups/forwarding-mappings/${userbotSessionId.value}`)
    if (response.data.status === 'success') {
      existingMappings.value = response.data.mappings
    } else {
      mappingError.value = 'Fehler beim Laden der Weiterleitungen'
    }
  } catch (err) {
    mappingError.value = 'Fehler beim Laden der Weiterleitungen: ' + (err.message || err)
  }
}

// 5. Mapping anlegen
const createMapping = async () => {
  if (!userbotSessionId.value || !selectedSourceGroup.value || !selectedTargetGroup.value) {
    mappingError.value = 'Session oder Gruppen nicht korrekt ausgewählt.'
    updateDebugVars({
      mappingError: mappingError.value,
      userbotSessionId: userbotSessionId.value,
      selectedSourceGroup: selectedSourceGroup.value,
      selectedTargetGroup: selectedTargetGroup.value
    }) // <--- Debug-Ausgabe ergänzen
    return { status: 'error', message: mappingError.value }
  }
  try {
    const mappingData = {
      userbot_session_id: userbotSessionId.value,
      source_group_id: selectedSourceGroup.value.id,
      target_group_id: selectedTargetGroup.value.id
    }
    const response = await api.post(`/groups/forwarding-mapping`, mappingData)
    console.log('API-Response (createMapping):', response.data)
    if (response.data.status === 'success') {
      await loadExistingMappings()
      mappingError.value = ''
      return response.data
    } else {
      mappingError.value = response.data.message || 'Fehler beim Speichern der Weiterleitung'
      return response.data
    }
  } catch (err) {
    mappingError.value = 'Fehler beim Speichern der Weiterleitung: ' + (err.message || err)
    console.error('API-Fehler (createMapping):', err)
    return { status: 'error', message: mappingError.value, error: err }
  }
}

// 6. Mapping umschalten
const toggleMapping = async (mapping) => {
  try {
    const response = await api.post(`/userbot/forwarding-mapping/${mapping.id}/toggle`)
    if (response.data.status === 'success') {
      await loadExistingMappings()
    } else {
      mappingError.value = response.data.message || 'Fehler beim Umschalten'
    }
  } catch (err) {
    mappingError.value = 'Fehler beim Umschalten: ' + (err.message || err)
  }
}

// 7. Mapping löschen
const deleteMapping = async (mapping) => {
  try {
    const response = await api.delete(`/userbot/forwarding-mapping/${mapping.id}`)
    if (response.data.status === 'success') {
      await loadExistingMappings()
    } else {
      mappingError.value = response.data.message || 'Fehler beim Löschen'
    }
  } catch (err) {
    mappingError.value = 'Fehler beim Löschen: ' + (err.message || err)
  }
}

// 8. Nach jeder Änderung alles neu laden
watch([userbotSessionId], async () => {
  await loadDialogs()
  await loadExistingMappings()
})

// 9. Nach erfolgreicher Session-Verifizierung Session-ID setzen
onMounted(async () => {
  let debugSet = false
  const storedSession = localStorage.getItem('userbot_session')
  if (storedSession) {
    userbotSession.value = JSON.parse(storedSession)
    // Setze phoneNumber automatisch aus der Session
    if (userbotSession.value && userbotSession.value.phone) {
      phoneNumber.value = userbotSession.value.phone
    }
    await loadGroups()
    await loadForwardings()
    debugSet = true
  } else {
    await loadExistingSession()
    debugSet = true
  }
  // Fallback: authStore.user aus wallstreet_session setzen, falls undefined
  if (!authStore.user) {
    const wsSession = localStorage.getItem('wallstreet_session')
    if (wsSession) {
      try {
        const wsData = JSON.parse(wsSession)
        authStore.user = {
          id: wsData.user_id,
          telegram_id: wsData.telegram_id,
          phone: wsData.phone,
          package_id: wsData.package_id,
          is_superadmin: wsData.is_superadmin,
          role: wsData.role,
          user_name: wsData.user_name,
          features: wsData.features || {}
        }
      } catch (e) {}
    }
  }
  if (!loadGroupsCalled) {
    debugInfo.value = `loadGroups wurde NICHT aufgerufen!\nUserbot-Session: ${JSON.stringify(userbotSession.value)}\nPaketdaten: ${JSON.stringify(authStore.user)}`
  }
  // Sofortige Debug-Ausgabe der Sessions beim Mount
  try {
    const mySessionsResult = await userbotAPI.getMySessions()
    updateDebugVars({ mySessionsResult })
  } catch (e) {}
})
</script>

<!-- Styles werden aus globaler index.css verwendet --> 