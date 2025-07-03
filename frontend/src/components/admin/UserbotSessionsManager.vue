<template>
  <div class="userbot-sessions-manager">
    <div class="header">
      <h2>🤖 Userbot-Sessions Verwaltung</h2>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <i class="fas fa-plus"></i> Neue Session
      </button>
    </div>

    <!-- Sessions Liste -->
    <div class="sessions-grid">
      <div v-for="session in sessions" :key="session.id" class="session-card">
        <div class="session-header">
          <h3>{{ session.session_name }}</h3>
          <div class="session-status" :class="{ active: session.is_active }">
            {{ session.is_active ? 'Aktiv' : 'Inaktiv' }}
          </div>
        </div>
        
        <div class="session-details">
          <div class="detail-item">
            <strong>Telefon:</strong> {{ session.phone }}
          </div>
          <div class="detail-item">
            <strong>Typ:</strong> {{ getSessionTypeLabel(session.session_type) }}
          </div>
          <div class="detail-item">
            <strong>User ID:</strong> {{ session.user_id }}
          </div>
          <div class="detail-item">
            <strong>Erstellt:</strong> {{ formatDate(session.created_at) }}
          </div>
        </div>
        
        <div class="session-actions">
          <button @click="editSession(session)" class="btn btn-secondary btn-sm">
            <i class="fas fa-edit"></i> Bearbeiten
          </button>
          <button @click="deleteSession(session.id)" class="btn btn-danger btn-sm">
            <i class="fas fa-trash"></i> Löschen
          </button>
        </div>
      </div>
    </div>

    <!-- Erstellen/Bearbeiten Modal -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ showEditModal ? 'Session bearbeiten' : 'Neue Session erstellen' }}</h3>
          <button @click="closeModal" class="btn-close">&times;</button>
        </div>
        
        <form @submit.prevent="saveSession" class="modal-form">
          <div class="form-group">
            <label for="user_id">User ID:</label>
            <input 
              id="user_id"
              v-model="formData.user_id" 
              type="number" 
              required 
              class="form-control"
            />
          </div>
          
          <div class="form-group">
            <label for="phone">Telefonnummer:</label>
            <input 
              id="phone"
              v-model="formData.phone" 
              type="tel" 
              required 
              class="form-control"
              placeholder="+49123456789"
            />
          </div>
          
          <div class="form-group">
            <label for="session_name">Session Name:</label>
            <input 
              id="session_name"
              v-model="formData.session_name" 
              type="text" 
              required 
              class="form-control"
              placeholder="z.B. Meine Weiterleitungen"
            />
          </div>
          
          <div class="form-group">
            <label for="session_type">Session Typ:</label>
            <select id="session_type" v-model="formData.session_type" required class="form-control">
              <option value="message_forwarding">Nachrichten-Weiterleitung</option>
              <option value="signal_groups">Signal-Gruppen Bot</option>
              <option value="auto_reply">Auto-Reply Bot</option>
              <option value="custom">Benutzerdefiniert</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="telegram_session_string">Telegram Session String (optional):</label>
            <textarea 
              id="telegram_session_string"
              v-model="formData.telegram_session_string" 
              class="form-control"
              rows="3"
              placeholder="Telegram Session String für diese Session"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="formData.is_active"
              />
              Session ist aktiv
            </label>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">
              Abbrechen
            </button>
            <button type="submit" class="btn btn-primary">
              {{ showEditModal ? 'Aktualisieren' : 'Erstellen' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Bestätigungs-Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="showDeleteModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Session löschen</h3>
          <button @click="showDeleteModal = false" class="btn-close">&times;</button>
        </div>
        
        <div class="modal-body">
          <p>Sind Sie sicher, dass Sie diese Userbot-Session löschen möchten?</p>
          <p><strong>{{ sessionToDelete?.session_name }}</strong></p>
        </div>
        
        <div class="modal-actions">
          <button @click="showDeleteModal = false" class="btn btn-secondary">
            Abbrechen
          </button>
          <button @click="confirmDelete" class="btn btn-danger">
            Löschen
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'UserbotSessionsManager',
  setup() {
    const authStore = useAuthStore()
    const sessions = ref([])
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const showDeleteModal = ref(false)
    const sessionToDelete = ref(null)
    const editingSession = ref(null)
    
    const formData = ref({
      user_id: '',
      phone: '',
      session_name: '',
      session_type: 'message_forwarding',
      telegram_session_string: '',
      is_active: true
    })

    const loadSessions = async () => {
      try {
        const response = await fetch('/api/admin/userbot-sessions', {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        if (response.ok) {
          sessions.value = await response.json()
        } else {
          console.error('Fehler beim Laden der Sessions')
        }
      } catch (error) {
        console.error('Fehler beim Laden der Sessions:', error)
      }
    }

    const saveSession = async () => {
      try {
        const url = showEditModal.value 
          ? `/api/admin/userbot-sessions/${editingSession.value.id}`
          : '/api/admin/userbot-sessions'
        
        const method = showEditModal.value ? 'PUT' : 'POST'
        
        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authStore.token}`
          },
          body: JSON.stringify(formData.value)
        })
        
        if (response.ok) {
          await loadSessions()
          closeModal()
        } else {
          console.error('Fehler beim Speichern der Session')
        }
      } catch (error) {
        console.error('Fehler beim Speichern der Session:', error)
      }
    }

    const editSession = (session) => {
      editingSession.value = session
      formData.value = {
        user_id: session.user_id,
        phone: session.phone,
        session_name: session.session_name,
        session_type: session.session_type,
        telegram_session_string: session.telegram_session_string || '',
        is_active: session.is_active
      }
      showEditModal.value = true
    }

    const deleteSession = (sessionId) => {
      sessionToDelete.value = sessions.value.find(s => s.id === sessionId)
      showDeleteModal.value = true
    }

    const confirmDelete = async () => {
      try {
        const response = await fetch(`/api/admin/userbot-sessions/${sessionToDelete.value.id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        if (response.ok) {
          await loadSessions()
          showDeleteModal.value = false
          sessionToDelete.value = null
        } else {
          console.error('Fehler beim Löschen der Session')
        }
      } catch (error) {
        console.error('Fehler beim Löschen der Session:', error)
      }
    }

    const closeModal = () => {
      showCreateModal.value = false
      showEditModal.value = false
      editingSession.value = null
      formData.value = {
        user_id: '',
        phone: '',
        session_name: '',
        session_type: 'message_forwarding',
        telegram_session_string: '',
        is_active: true
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

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('de-DE', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    onMounted(() => {
      loadSessions()
    })

    return {
      sessions,
      showCreateModal,
      showEditModal,
      showDeleteModal,
      sessionToDelete,
      formData,
      saveSession,
      editSession,
      deleteSession,
      confirmDelete,
      closeModal,
      getSessionTypeLabel,
      formatDate
    }
  }
}
</script>

<style scoped>
.userbot-sessions-manager {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header h2 {
  margin: 0;
  color: #333;
}

.sessions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.session-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.session-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.1rem;
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

.detail-item {
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.detail-item strong {
  color: #555;
  min-width: 80px;
  display: inline-block;
}

.session-actions {
  display: flex;
  gap: 10px;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.8rem;
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

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  margin: 0;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.modal-body {
  padding: 20px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding: 20px;
  border-top: 1px solid #e0e0e0;
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

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #545b62;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover {
  background: #c82333;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}
</style> 