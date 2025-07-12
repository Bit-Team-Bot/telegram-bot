<template>
  <div class="dashboard-container">
    <!-- Header Section -->
    <div class="header-section">
      <img src="@/assets/wallstreet-header.png" alt="Wallstreet Crypto Header" class="header-image" />

    </div>
    
    <!-- Main Content -->
    <div class="main-content">
      <div class="user-manager">
        <div class="manager-header">
          <h1 class="manager-title">Benutzerverwaltung</h1>
          <button @click="showAddUserModal = true" class="add-button">
            <svg class="button-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            Benutzer hinzufügen
          </button>
        </div>

        <div class="search-container">
          <div class="search-wrapper">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Benutzer suchen..."
              class="search-input"
            />
            <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
          </div>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Email</th>
                <th>Rolle</th>
                <th>Status</th>
                <th>Aktionen</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id">
                <td>{{ user.id }}</td>
                <td>{{ user.username }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user.role }}</td>
                <td>
                  <span :class="['status-badge', user.status === 'active' ? 'status-active' : 'status-inactive']">
                    {{ user.status }}
                  </span>
                </td>
                <td>
                  <button @click="editUser(user)" class="action-button edit">Bearbeiten</button>
                  <button @click="deleteUser(user.id)" class="action-button delete">Löschen</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Add User Modal -->
        <div v-if="showAddUserModal" class="modal-overlay" @click="showAddUserModal = false">
          <div class="modal-content" @click.stop>
            <h2 class="modal-title">Benutzer hinzufügen</h2>
            <form @submit.prevent="addUser" class="modal-form">
              <div class="form-group">
                <label for="username" class="form-label">Username</label>
                <input
                  id="username"
                  v-model="newUser.username" 
                  type="text"
                  required
                  class="form-input"
                />
              </div>
              
              <div class="form-group">
                <label for="email" class="form-label">Email</label>
                <input 
                  id="email"
                  v-model="newUser.email" 
                  type="email" 
                  required
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label for="password" class="form-label">Passwort</label>
                <input
                  id="password"
                  v-model="newUser.password" 
                  type="password" 
                  required
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label for="role" class="form-label">Rolle</label>
                <select
                  id="role"
                  v-model="newUser.role" 
                  required
                  class="form-select"
                >
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                  <option value="partner">Partner</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">Status</label>
                <div class="checkbox-group">
                  <label class="checkbox-label">
                    <input
                      type="checkbox"
                      v-model="newUser.is_active"
                      class="checkbox-input"
                    />
                    Aktiv
                  </label>
                </div>
              </div>

              <div class="modal-actions">
                <button type="button" @click="showAddUserModal = false" class="cancel-button">
                  Abbrechen
                </button>
                <button type="submit" class="submit-button">
                  Hinzufügen
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Back to Dashboard Section -->
    <div class="back-section">
      <BaseButton @click="$router.push('/dashboard')">
        Zurück zum Dashboard
      </BaseButton>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'
import BaseCard from '../../components/BaseCard.vue'
import BaseButton from '../../components/BaseButton.vue'
import { useToast } from 'vue-toastification'

export default {
  name: 'UserManager',
  
  components: {
    BaseCard,
    BaseButton
  },
  
  setup() {
    const toast = useToast()
    const users = ref([])
    const packages = ref([])
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const searchQuery = ref('')
    const currentUser = ref({
      telegram_id: '',
      phone: '',
      package_id: '',
      is_superadmin: false
    })
    const showAddUserModal = ref(false)
    const newUser = ref({
      username: '',
      email: '',
      password: '',
      role: 'user',
      is_active: true
    })

    const filteredUsers = computed(() => {
      if (!searchQuery.value) return users.value
      
      const query = searchQuery.value.toLowerCase()
      return users.value.filter(user => 
        user.telegram_id.toLowerCase().includes(query) ||
        user.phone.toLowerCase().includes(query)
      )
    })

    const loadUsers = async () => {
      try {
        const response = await api.get('/admin/users')
        users.value = response.data
      } catch (error) {
        toast.error('Fehler beim Laden der Benutzer')
        console.error('Fehler beim Laden der Benutzer:', error)
      }
    }

    const loadPackages = async () => {
      try {
        const response = await api.get('/admin/packages')
        packages.value = response.data
      } catch (error) {
        toast.error('Fehler beim Laden der Pakete')
        console.error('Fehler beim Laden der Pakete:', error)
      }
    }

    const editUser = (user) => {
      currentUser.value = { ...user }
      showEditModal.value = true
    }

    const toggleUserStatus = async (user) => {
      try {
        await api.put(`/admin/users/${user.id}/toggle-status`)
        await loadUsers()
        toast.success(`Benutzer ${user.is_active ? 'deaktiviert' : 'aktiviert'}`)
      } catch (error) {
        toast.error('Fehler beim Ändern des Benutzerstatus')
        console.error('Fehler beim Ändern des Benutzerstatus:', error)
      }
    }

    const saveUser = async () => {
      try {
        if (showEditModal.value) {
          await api.put(`/admin/users/${currentUser.value.id}`, currentUser.value)
          toast.success('Benutzer erfolgreich aktualisiert')
        } else {
          await api.post('/admin/users', currentUser.value)
          toast.success('Benutzer erfolgreich erstellt')
        }
        await loadUsers()
        closeModal()
      } catch (error) {
        const message = error.response?.data?.detail || 'Fehler beim Speichern des Benutzers'
        toast.error(message)
        console.error('Fehler beim Speichern des Benutzers:', error)
      }
    }

    const closeModal = () => {
      showCreateModal.value = false
      showEditModal.value = false
      currentUser.value = {
        telegram_id: '',
        phone: '',
        package_id: '',
        is_superadmin: false
      }
    }

    const addUser = async () => {
      try {
        await api.post('/admin/users', newUser.value)
        toast.success('Benutzer erfolgreich hinzugefügt')
        showAddUserModal.value = false
        await loadUsers()
      } catch (error) {
        const message = error.response?.data?.detail || 'Fehler beim Hinzufügen des Benutzers'
        toast.error(message)
        console.error('Fehler beim Hinzufügen des Benutzers:', error)
      }
    }

    const deleteUser = async (id) => {
      try {
        await api.delete(`/admin/users/${id}`)
        toast.success('Benutzer erfolgreich gelöscht')
        await loadUsers()
      } catch (error) {
        toast.error('Fehler beim Löschen des Benutzers')
        console.error('Fehler beim Löschen des Benutzers:', error)
      }
    }

    onMounted(() => {
      loadUsers()
      loadPackages()
    })

    return {
      users,
      packages,
      showCreateModal,
      showEditModal,
      searchQuery,
      currentUser,
      filteredUsers,
      editUser,
      toggleUserStatus,
      saveUser,
      closeModal,
      showAddUserModal,
      newUser,
      addUser,
      deleteUser
    }
  }
}
</script>

<!-- Styles werden aus globaler index.css verwendet --> 