<template>
  <div class="dashboard-container">
    <!-- Header Section -->
    <div class="header-section">
      <img src="@/assets/wallstreet-header.png" alt="Wallstreet Crypto Header" class="header-image" />
    </div>
    <div class="main-content">
      <!-- Page Header (zentriert, globaler Style) -->
      <div class="page-header">
        <h1 class="page-title">Userbot-Sessions Verwaltung</h1>
        <p class="page-subtitle">Verwalte alle Userbot-Sessions im System</p>
      </div>
      <div class="user-role-box">
        <div class="role-content">
          <div class="role-section">
            <button @click="loadSessions" class="role-btn admin">
              <span class="role-icon">🔄</span>
              <span class="role-text">Aktualisieren</span>
            </button>
          </div>
        </div>
      </div>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Telefon</th>
              <th>Telegram-ID</th>
              <th>Name</th>
              <th>Typ</th>
              <th>Status</th>
              <th>Aktionen</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="session in sessions" :key="session.id">
              <td>{{ session.id }}</td>
              <td>{{ session.phone }}</td>
              <td>{{ session.telegram_id }}</td>
              <td>{{ session.session_name }}</td>
              <td>{{ session.session_type }}</td>
              <td>
                <span :class="['status-badge', session.is_active ? 'status-active' : 'status-inactive']">
                  {{ session.is_active ? 'Aktiv' : 'Inaktiv' }}
                </span>
              </td>
              <td>
                <button @click="editSession(session)" class="action-button edit">Bearbeiten</button>
                <button @click="toggleSession(session)" class="action-button toggle">
                  {{ session.is_active ? 'Deaktivieren' : 'Aktivieren' }}
                </button>
                <button @click="deleteSession(session)" class="action-button delete">Löschen</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- Edit Modal -->
      <div v-if="showEditModal" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <h2 class="modal-title">Session bearbeiten</h2>
          <form @submit.prevent="saveSession" class="modal-form">
            <div class="form-group">
              <label class="form-label">Telefon</label>
              <input v-model="editingSession.phone" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Telegram-ID</label>
              <input v-model="editingSession.telegram_id" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Name</label>
              <input v-model="editingSession.session_name" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Typ</label>
              <input v-model="editingSession.session_type" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Status</label>
              <select v-model="editingSession.is_active" class="form-select">
                <option :value="true">Aktiv</option>
                <option :value="false">Inaktiv</option>
              </select>
            </div>
            <div class="modal-actions">
              <button type="button" @click="closeModal" class="cancel-button">Abbrechen</button>
              <button type="submit" class="submit-button">Speichern</button>
            </div>
          </form>
        </div>
      </div>
    </div>
    <div class="back-section">
      <BaseButton @click="$router.push('/admin-dashboard')">
        Zurück zum Admin-Dashboard
      </BaseButton>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import BaseButton from '../../components/BaseButton.vue'
import { useToast } from 'vue-toastification'

const toast = useToast()
const sessions = ref([])
const showEditModal = ref(false)
const editingSession = ref({})

const loadSessions = async () => {
  try {
    const response = await axios.get('/admin/userbot-sessions')
    sessions.value = response.data
    toast.success('Sessions geladen')
  } catch (error) {
    toast.error('Fehler beim Laden der Sessions')
  }
}

const editSession = (session) => {
  editingSession.value = { ...session }
  showEditModal.value = true
}

const saveSession = async () => {
  try {
    await axios.put(`/admin/userbot-sessions/${editingSession.value.id}`, editingSession.value)
    toast.success('Session gespeichert')
    showEditModal.value = false
    await loadSessions()
  } catch (error) {
    toast.error('Fehler beim Speichern')
  }
}

const toggleSession = async (session) => {
  try {
    await axios.put(`/admin/userbot-sessions/${session.id}`, { ...session, is_active: !session.is_active })
    toast.success('Status geändert')
    await loadSessions()
  } catch (error) {
    toast.error('Fehler beim Ändern des Status')
  }
}

const deleteSession = async (session) => {
  if (!confirm('Wirklich löschen?')) return
  try {
    await axios.delete(`/admin/userbot-sessions/${session.id}`)
    toast.success('Session gelöscht')
    await loadSessions()
  } catch (error) {
    toast.error('Fehler beim Löschen')
  }
}

const closeModal = () => {
  showEditModal.value = false
  editingSession.value = {}
}

onMounted(() => {
  loadSessions()
})
</script>

<!-- Styles werden aus globaler index.css verwendet --> 