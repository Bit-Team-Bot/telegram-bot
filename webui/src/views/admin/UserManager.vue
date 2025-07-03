<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Zurück-Button und Header -->
    <div class="flex items-center justify-between mb-8">
      <div class="flex items-center space-x-4">
        <button
          @click="$router.push('/dashboard')"
          class="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
          </svg>
          <span>Zurück zum Dashboard</span>
        </button>
        <h1 class="text-2xl font-bold">Benutzer verwalten</h1>
      </div>
      
      <button
        @click="showCreateModal = true"
        class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors"
      >
        Neuen Benutzer erstellen
      </button>
    </div>

    <!-- Suchleiste -->
    <div class="mb-6">
      <div class="relative">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Benutzer suchen (Telegram ID oder Telefonnummer)..."
          class="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
        <svg class="absolute left-3 top-2.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
      </div>
    </div>

    <!-- Benutzer-Tabelle -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Telegram ID</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Telefonnummer</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Paket</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Admin</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Aktionen</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="user in filteredUsers" :key="user.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm font-medium text-gray-900">{{ user.telegram_id }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-900">{{ user.phone }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                {{ getPackageName(user.package_id) }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="['px-2 py-1 rounded-full text-xs', user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800']">
                {{ user.is_active ? 'Aktiv' : 'Inaktiv' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="['px-2 py-1 rounded-full text-xs', user.is_superadmin ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800']">
                {{ user.is_superadmin ? 'Superadmin' : 'User' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <button
                @click="editUser(user)"
                class="text-blue-600 hover:text-blue-900 mr-3 transition-colors"
              >
                Bearbeiten
              </button>
              <button
                @click="toggleUserStatus(user)"
                :class="['mr-3 transition-colors', user.is_active ? 'text-orange-600 hover:text-orange-900' : 'text-green-600 hover:text-green-900']"
              >
                {{ user.is_active ? 'Deaktivieren' : 'Aktivieren' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal für Benutzer erstellen/bearbeiten -->
    <div v-if="showCreateModal || showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">
          {{ showEditModal ? 'Benutzer bearbeiten' : 'Neuer Benutzer' }}
        </h2>

        <form @submit.prevent="saveUser" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Telegram ID</label>
            <input
              v-model="currentUser.telegram_id"
              type="text"
              required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">Telefonnummer</label>
            <input
              v-model="currentUser.phone"
              type="tel"
              required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">Paket</label>
            <select
              v-model="currentUser.package_id"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">Kein Paket</option>
              <option v-for="pkg in packages" :key="pkg.id" :value="pkg.id">
                {{ pkg.name }} ({{ pkg.price }} BUSD)
              </option>
            </select>
          </div>

          <div class="flex items-center">
            <input
              v-model="currentUser.is_superadmin"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            >
            <label class="ml-2 block text-sm text-gray-900">
              Administrator
            </label>
          </div>

          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="closeModal"
              class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Abbrechen
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Speichern
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useToast } from 'vue-toastification'

export default {
  name: 'UserManager',
  
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
        const response = await axios.get('/api/admin/users')
        users.value = response.data
      } catch (error) {
        toast.error('Fehler beim Laden der Benutzer')
        console.error('Fehler beim Laden der Benutzer:', error)
      }
    }

    const loadPackages = async () => {
      try {
        const response = await axios.get('/api/packages')
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
        await axios.put(`/api/admin/users/${user.id}/toggle-status`)
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
          await axios.put(`/api/admin/users/${currentUser.value.id}`, currentUser.value)
          toast.success('Benutzer erfolgreich aktualisiert')
        } else {
          await axios.post('/api/admin/users', currentUser.value)
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
      closeModal
    }
  }
}
</script> 