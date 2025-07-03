<template>
  <div class="userbot-sessions">
    <div class="header">
      <h2>🤖 Userbot-Sessions</h2>
      <p class="subtitle">Verwalte deine Telegram-Bot-Sessions für verschiedene Funktionen</p>
    </div>

    <!-- Kein Paket Nachricht -->
    <div v-if="showNoPackageMessage" class="no-package-message">
      <div class="message-content">
        <div class="message-icon">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <h3>Kein aktives Userbot-Paket</h3>
        <p>Sie benötigen ein aktives Userbot-Paket, um Sessions zu erstellen und zu verwalten.</p>
        <div class="message-actions">
          <button @click="goToPackages" class="btn btn-primary">
            <i class="fas fa-shopping-cart"></i>
            Pakete anzeigen
          </button>
        </div>
      </div>
    </div>

    <!-- Bestehende Sessions -->
    <div class="sessions-overview" v-if="userSessions.length > 0">
      <h3>Deine Sessions</h3>
      <div class="sessions-grid">
        <div 
          v-for="session in userSessions" 
          :key="session.id" 
          class="session-card"
        >
          <div class="session-header">
            <div class="session-info">
              <h3>{{ session.session_name }}</h3>
              <span class="session-type">{{ getSessionTypeLabel(session.session_type) }}</span>
            </div>
            <span 
              class="session-status"
              :class="{ active: session.is_active }"
            >
              {{ session.is_active ? 'Aktiv' : 'Inaktiv' }}
            </span>
          </div>
          
          <div class="session-details">
            <div class="detail-row">
              <span class="label">Handynummer:</span>
              <span class="value">{{ session.phone }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Erstellt:</span>
              <span class="value">{{ formatDate(session.created_at) }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Abonnement-Status:</span>
              <span class="value subscription-status" :class="session.subscription_status">
                {{ getSubscriptionStatusLabel(session.subscription_status) }}
              </span>
            </div>
            <div class="detail-row" v-if="session.subscription_end_date">
              <span class="label">Ablaufdatum:</span>
              <span class="value" :class="getExpiryClass(session.subscription_end_date)">
                {{ formatDate(session.subscription_end_date) }}
                <span v-if="getDaysUntilExpiry(session.subscription_end_date) > 0" class="days-remaining">
                  ({{ getDaysUntilExpiry(session.subscription_end_date) }} Tage)
                </span>
                <span v-else-if="getDaysUntilExpiry(session.subscription_end_date) < 0" class="days-overdue">
                  ({{ Math.abs(getDaysUntilExpiry(session.subscription_end_date)) }} Tage überfällig)
                </span>
              </span>
            </div>
            <div class="detail-row" v-if="session.auto_delete_date">
              <span class="label">Löschung:</span>
              <span class="value" :class="getDeletionClass(session.auto_delete_date)">
                {{ formatDate(session.auto_delete_date) }}
                <span v-if="getDaysUntilDeletion(session.auto_delete_date) > 0" class="days-remaining">
                  ({{ getDaysUntilDeletion(session.auto_delete_date) }} Tage)
                </span>
              </span>
            </div>
            <div v-if="session.config_data" class="detail-row">
              <span class="label">Konfiguration:</span>
              <span class="value config-preview">{{ getConfigPreview(session.config_data) }}</span>
            </div>
          </div>
          
          <div class="session-actions">
            <button @click="editSession(session)" class="btn btn-secondary">
              Bearbeiten
            </button>
            <button 
              @click="toggleSession(session)" 
              :class="['btn', session.is_active ? 'btn-warning' : 'btn-success']"
              :disabled="session.subscription_status === 'expired' || session.subscription_status === 'pending_payment'"
            >
              {{ session.is_active ? 'Deaktivieren' : 'Aktivieren' }}
            </button>
            <button 
              v-if="session.subscription_status === 'expired' || session.subscription_status === 'pending_payment'"
              @click="extendSession(session)" 
              class="btn btn-primary"
            >
              Verlängern
            </button>
            <button @click="deleteSession(session)" class="btn btn-danger">
              Löschen
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Session erstellen -->
    <div class="create-section">
      <h3>Neue Session erstellen</h3>
      <div class="session-types">
        <div class="session-type-card" @click="createSession('message_forwarding')">
          <div class="type-icon">
            <i class="fas fa-share-alt"></i>
          </div>
          <h4>Nachrichten-Weiterleitung</h4>
          <p>Leiten Sie Nachrichten automatisch zwischen Gruppen weiter</p>
          <div class="type-features">
            <span class="feature-tag">Quellgruppen</span>
            <span class="feature-tag">Zielgruppen</span>
            <span class="feature-tag">Filter</span>
          </div>
        </div>
        
        <div class="session-type-card" @click="createSession('signal_groups')">
          <div class="type-icon">
            <i class="fas fa-broadcast-tower"></i>
          </div>
          <h4>Signal-Gruppen Bot</h4>
          <p>Automatische Weiterleitung in Signalgruppen (System-verwaltet)</p>
          <div class="type-features">
            <span class="feature-tag">Auto-Erstellung</span>
            <span class="feature-tag">System-Gruppen</span>
            <span class="feature-tag">Partner-Integration</span>
          </div>
        </div>
        
        <div class="session-type-card" @click="createSession('auto_reply')">
          <div class="type-icon">
            <i class="fas fa-reply"></i>
          </div>
          <h4>Auto-Reply Bot</h4>
          <p>Automatische Antworten auf Nachrichten</p>
          <div class="type-features">
            <span class="feature-tag">Trigger-Keywords</span>
            <span class="feature-tag">Antworten</span>
            <span class="feature-tag">Verzögerung</span>
          </div>
        </div>
        
        <div class="session-type-card" @click="createSession('custom')">
          <div class="type-icon">
            <i class="fas fa-cogs"></i>
          </div>
          <h4>Benutzerdefiniert</h4>
          <p>Eigene Bot-Funktionen implementieren</p>
          <div class="type-features">
            <span class="feature-tag">Custom Script</span>
            <span class="feature-tag">Parameter</span>
            <span class="feature-tag">Flexibel</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Session erstellen Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Neue Session: {{ getSessionTypeLabel(selectedSessionType) }}</h3>
          <button @click="closeModal" class="btn-close">&times;</button>
        </div>
        
        <form @submit.prevent="saveSession" class="modal-form">
          <div class="form-group">
            <label>Session Name</label>
            <input 
              v-model="formData.session_name" 
              type="text" 
              class="form-control"
              :placeholder="getSessionNamePlaceholder()"
              required
            />
          </div>
          
          <div class="form-group">
            <label>Handynummer</label>
            <input 
              v-model="formData.phone" 
              type="tel" 
              class="form-control"
              placeholder="+49123456789"
              required
            />
            <small class="form-help">Format: +49 für Deutschland</small>
          </div>
          
          <div class="form-group">
            <label>Telegram Session String (optional)</label>
            <textarea 
              v-model="formData.telegram_session_string" 
              class="form-control"
              rows="3"
              placeholder="1BQANOTEzOTUxNDU..."
            ></textarea>
            <small class="form-help">Lassen Sie leer für automatische Session-Erstellung</small>
          </div>
          
          <!-- Spezifische Konfiguration je nach Session-Typ -->
          <div v-if="selectedSessionType === 'message_forwarding'" class="session-config">
            <h4>Weiterleitungs-Konfiguration</h4>
            <div class="form-group">
              <label>Quellgruppen (IDs)</label>
              <input 
                v-model="configData.source_groups" 
                type="text" 
                class="form-control"
                placeholder="-1001234567890, -1001234567891"
              />
            </div>
            <div class="form-group">
              <label>Zielgruppen (IDs)</label>
              <input 
                v-model="configData.target_groups" 
                type="text" 
                class="form-control"
                placeholder="-1001234567890, -1001234567891"
              />
            </div>
          </div>
          
          <div v-if="selectedSessionType === 'signal_groups'" class="session-config">
            <h4>Signal-Gruppen-Konfiguration</h4>
            <div class="form-group">
              <label>Signal-Gruppe auswählen</label>
              <select v-model="configData.signal_group_id" class="form-control">
                <option value="">Signal-Gruppe auswählen...</option>
                <option v-for="group in signalGroups" :key="group.id" :value="group.id">
                  {{ group.name }}
                </option>
              </select>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">
              Abbrechen
            </button>
            <button type="submit" class="btn btn-primary">
              Session erstellen
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Session bearbeiten Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Session bearbeiten</h3>
          <button @click="closeModal" class="btn-close">&times;</button>
        </div>
        
        <form @submit.prevent="updateSession" class="modal-form">
          <div class="form-group">
            <label>Session Name</label>
            <input 
              v-model="editFormData.session_name" 
              type="text" 
              class="form-control"
              required
            />
          </div>
          
          <div class="form-group">
            <label>Handynummer</label>
            <input 
              v-model="editFormData.phone" 
              type="tel" 
              class="form-control"
              required
            />
          </div>
          
          <div class="form-group">
            <label>Telegram Session String</label>
            <textarea 
              v-model="editFormData.telegram_session_string" 
              class="form-control"
              rows="3"
            ></textarea>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">
              Abbrechen
            </button>
            <button type="submit" class="btn btn-primary">
              Aktualisieren
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'UserbotSessions',
  setup() {
    const authStore = useAuthStore()
    const userSessions = ref([])
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const showNoPackageMessage = ref(false)
    const selectedSessionType = ref('')
    const editingSession = ref(null)
    
    const formData = ref({
      phone: '',
      session_name: '',
      session_type: '',
      telegram_session_string: '',
      is_active: true
    })
    
    const editFormData = ref({
      phone: '',
      session_name: '',
      telegram_session_string: ''
    })

    const configData = ref({
      source_groups: '',
      target_groups: '',
      signal_group_id: ''
    })

    const signalGroups = ref([])

    const loadUserSessions = async () => {
      try {
        const response = await fetch('/api/user/userbot-sessions', {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        if (response.ok) {
          userSessions.value = await response.json()
        } else if (response.status === 403) {
          // User hat kein aktives Userbot-Paket
          userSessions.value = []
          showNoPackageMessage.value = true
        } else {
          console.error('Fehler beim Laden der Sessions')
        }
      } catch (error) {
        console.error('Fehler beim Laden der Sessions:', error)
      }
    }

    const createSession = (sessionType) => {
      selectedSessionType.value = sessionType
      formData.value.session_type = sessionType
      showCreateModal.value = true
    }

    const saveSession = async () => {
      try {
        const response = await fetch('/api/user/userbot-sessions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authStore.token}`
          },
          body: JSON.stringify(formData.value)
        })
        
        if (response.ok) {
          await loadUserSessions()
          closeModal()
        } else {
          console.error('Fehler beim Erstellen der Session')
        }
      } catch (error) {
        console.error('Fehler beim Erstellen der Session:', error)
      }
    }

    const editSession = (session) => {
      editingSession.value = session
      editFormData.value = {
        phone: session.phone,
        session_name: session.session_name,
        telegram_session_string: session.telegram_session_string || ''
      }
      showEditModal.value = true
    }

    const updateSession = async () => {
      try {
        const response = await fetch(`/api/user/userbot-sessions/${editingSession.value.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authStore.token}`
          },
          body: JSON.stringify(editFormData.value)
        })
        
        if (response.ok) {
          await loadUserSessions()
          closeModal()
        } else {
          console.error('Fehler beim Aktualisieren der Session')
        }
      } catch (error) {
        console.error('Fehler beim Aktualisieren der Session:', error)
      }
    }

    const toggleSession = async (session) => {
      try {
        const response = await fetch(`/api/user/userbot-sessions/${session.id}/toggle`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        if (response.ok) {
          await loadUserSessions()
        } else {
          console.error('Fehler beim Umschalten der Session')
        }
      } catch (error) {
        console.error('Fehler beim Umschalten der Session:', error)
      }
    }

    const closeModal = () => {
      showCreateModal.value = false
      showEditModal.value = false
      editingSession.value = null
      selectedSessionType.value = ''
      formData.value = {
        phone: '',
        session_name: '',
        session_type: '',
        telegram_session_string: '',
        is_active: true
      }
      configData.value = {
        source_groups: '',
        target_groups: '',
        signal_group_id: ''
      }
    }

    const getSessionTypeLabel = (type) => {
      const labels = {
        'message_forwarding': 'Nachrichten-Weiterleitung',
        'signal_groups': 'Signal-Gruppen Bot',
        'auto_reply': 'Auto-Reply Bot',
        'custom': 'Benutzerdefiniert'
      }
      return labels[type] || type
    }

    const getSessionNamePlaceholder = () => {
      const placeholders = {
        'message_forwarding': 'z.B. Meine Weiterleitungen',
        'signal_groups': 'z.B. Signal-Gruppen Bot',
        'auto_reply': 'z.B. Auto-Reply Bot',
        'custom': 'z.B. Mein Custom Bot'
      }
      return placeholders[selectedSessionType.value] || 'Session Name'
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('de-DE', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const getConfigPreview = (config) => {
      // Implementieren Sie hier die Logik zur Vorschau der Konfiguration
      return JSON.stringify(config).substring(0, 50) + '...'
    }

    const checkUserbotPackageStatus = async () => {
      try {
        const response = await fetch('/api/user/userbot-package-status', {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          if (!data.has_userbot_package) {
            showNoPackageMessage.value = true
          }
        }
      } catch (error) {
        console.error('Fehler beim Prüfen des Paket-Status:', error)
      }
    }

    const goToPackages = () => {
      // Navigation zu den Paketen (kann angepasst werden je nach Router-Struktur)
      window.location.href = '/packages'
    }

    const loadSignalGroups = async () => {
      try {
        const response = await fetch('/api/user/signal-groups', {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        if (response.ok) {
          signalGroups.value = await response.json()
        } else {
          console.error('Fehler beim Laden der Signalgruppen')
        }
      } catch (error) {
        console.error('Fehler beim Laden der Signalgruppen:', error)
      }
    }

    const getSubscriptionStatusLabel = (status) => {
      const labels = {
        'active': 'Aktiv',
        'expired': 'Abgelaufen',
        'pending_payment': 'Zahlung ausstehend'
      }
      return labels[status] || status
    }

    const getExpiryClass = (endDate) => {
      const days = getDaysUntilExpiry(endDate)
      if (days < 0) return 'expired'
      if (days <= 7) return 'expiring-soon'
      return 'active'
    }

    const getDeletionClass = (deleteDate) => {
      const days = getDaysUntilDeletion(deleteDate)
      if (days <= 3) return 'deletion-warning'
      return 'normal'
    }

    const getDaysUntilExpiry = (endDate) => {
      const now = new Date()
      const end = new Date(endDate)
      const diffTime = end - now
      return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    }

    const getDaysUntilDeletion = (deleteDate) => {
      const now = new Date()
      const deleteDateObj = new Date(deleteDate)
      const diffTime = deleteDateObj - now
      return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    }

    const extendSession = async (session) => {
      // Hier würde die Zahlungslogik implementiert werden
      const months = 1
      const paymentAmount = 29.99
      
      try {
        const response = await fetch(`/api/user/userbot-sessions/${session.id}/extend`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authStore.token}`
          },
          body: JSON.stringify({
            months: months,
            payment_amount: paymentAmount
          })
        })
        
        if (response.ok) {
          await loadUserSessions()
          alert('Session erfolgreich verlängert!')
        } else {
          const error = await response.json()
          alert(`Fehler: ${error.detail}`)
        }
      } catch (error) {
        console.error('Fehler beim Verlängern der Session:', error)
        alert('Fehler beim Verlängern der Session')
      }
    }

    onMounted(() => {
      checkUserbotPackageStatus()
      loadUserSessions()
      loadSignalGroups()
    })

    return {
      userSessions,
      showCreateModal,
      showEditModal,
      showNoPackageMessage,
      formData,
      editFormData,
      configData,
      signalGroups,
      createSession,
      saveSession,
      editSession,
      updateSession,
      toggleSession,
      closeModal,
      getSessionTypeLabel,
      getSessionNamePlaceholder,
      formatDate,
      getConfigPreview,
      loadSignalGroups,
      getSubscriptionStatusLabel,
      getExpiryClass,
      getDeletionClass,
      getDaysUntilExpiry,
      getDaysUntilDeletion,
      goToPackages,
      extendSession
    }
  }
}
</script>

<style scoped>
.userbot-sessions {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.header h2 {
  color: #333;
  margin-bottom: 10px;
}

.subtitle {
  color: #666;
  font-size: 1.1rem;
}

.sessions-overview {
  margin-bottom: 40px;
}

.sessions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.session-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.session-info h3 {
  margin: 0 0 5px 0;
  color: #333;
}

.session-type {
  color: #666;
  font-size: 0.9rem;
}

.session-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  background: #f0f0f0;
  color: #666;
}

.session-status.active {
  background: #e8f5e8;
  color: #2d5a2d;
}

.session-details {
  margin-bottom: 20px;
}

.detail-row {
  display: flex;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.label {
  font-weight: 500;
  color: #555;
  min-width: 120px;
}

.value {
  color: #333;
}

.session-string {
  font-family: monospace;
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
}

.session-actions {
  display: flex;
  gap: 10px;
}

.create-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.create-section h3 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.session-types {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.session-type-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.session-type-card:hover {
  background: #e9ecef;
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.15);
}

.type-icon {
  font-size: 2.5rem;
  color: #007bff;
  margin-bottom: 15px;
}

.session-type-card h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 1.2rem;
}

.session-type-card p {
  margin: 0 0 15px 0;
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
}

.type-features {
  margin-top: auto;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px;
}

.feature-tag {
  padding: 4px 8px;
  border-radius: 12px;
  background: #e3f2fd;
  color: #1976d2;
  font-size: 0.75rem;
  font-weight: 500;
}

/* Responsive Design */
@media (min-width: 768px) {
  .session-types {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1200px) {
  .session-types {
    grid-template-columns: repeat(2, 1fr);
    max-width: 800px;
  }
}

@media (max-width: 767px) {
  .session-types {
    grid-template-columns: 1fr;
  }
  
  .session-type-card {
    min-height: 180px;
    padding: 20px;
  }
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-form {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.form-control:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.form-help {
  display: block;
  margin-top: 5px;
  font-size: 0.8rem;
  color: #666;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

/* Abonnement-Status Styles */
.subscription-status {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.subscription-status.active {
  background: #d4edda;
  color: #155724;
}

.subscription-status.expired {
  background: #f8d7da;
  color: #721c24;
}

.subscription-status.pending_payment {
  background: #fff3cd;
  color: #856404;
}

.days-remaining {
  color: #28a745;
  font-size: 0.8rem;
  font-weight: 500;
}

.days-overdue {
  color: #dc3545;
  font-size: 0.8rem;
  font-weight: 500;
}

.value.expired {
  color: #dc3545;
}

.value.expiring-soon {
  color: #ffc107;
}

.value.deletion-warning {
  color: #dc3545;
  font-weight: bold;
}

.value.normal {
  color: #333;
}

/* Button Styles */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #545b62;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #1e7e34;
}

.btn-warning {
  background: #ffc107;
  color: #212529;
}

.btn-warning:hover:not(:disabled) {
  background: #e0a800;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c82333;
}

.session-config {
  margin-top: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
}

.session-config h4 {
  margin-bottom: 10px;
  color: #333;
}

/* Kein Paket Nachricht Styles */
.no-package-message {
  margin: 40px 0;
  padding: 40px;
  background: linear-gradient(135deg, #fff5f5 0%, #fef2f2 100%);
  border: 2px solid #fecaca;
  border-radius: 16px;
  text-align: center;
}

.message-content {
  max-width: 500px;
  margin: 0 auto;
}

.message-icon {
  font-size: 48px;
  color: #f59e0b;
  margin-bottom: 20px;
}

.message-content h3 {
  color: #dc2626;
  margin-bottom: 15px;
  font-size: 24px;
}

.message-content p {
  color: #6b7280;
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 30px;
}

.message-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.message-actions .btn {
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
}
</style> 