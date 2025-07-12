<template>
  <div class="dashboard-container">
    <!-- Header Section -->
    <div class="header-section">
      <img src="@/assets/wallstreet-header.png" alt="Wallstreet Crypto Header" class="header-image" />

    </div>
    
    <!-- Main Content -->
    <div class="main-content">
      <div class="partner-manager">
        <div class="manager-header">
          <h1 class="manager-title">Partnerverwaltung</h1>
          <button @click="showAddPartnerModal = true" class="add-button">
            <svg class="button-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            Partner hinzufügen
          </button>
        </div>

        <div class="tabs-container">
          <div class="tabs">
            <button 
              @click="activeTab = 'partners'" 
              :class="['tab-button', activeTab === 'partners' ? 'tab-active' : '']"
            >
              Partner
            </button>
            <button
              @click="activeTab = 'users'" 
              :class="['tab-button', activeTab === 'users' ? 'tab-active' : '']"
            >
              Benutzer
            </button>
            <button
              @click="activeTab = 'payments'" 
              :class="['tab-button', activeTab === 'payments' ? 'tab-active' : '']"
            >
              Zahlungen
            </button>
          </div>
        </div>

        <!-- Partners Tab -->
        <div v-if="activeTab === 'partners'" class="tab-content">
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Telegram</th>
                  <th>Status</th>
                  <th>Aktionen</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="partner in partners" :key="partner.id">
                  <td>{{ partner.id }}</td>
                  <td>{{ partner.name }}</td>
                  <td>{{ partner.email }}</td>
                  <td>{{ partner.telegram_id }}</td>
                  <td>
                    <span :class="['status-badge', partner.is_active ? 'status-active' : 'status-inactive']">
                      {{ partner.is_active ? 'Aktiv' : 'Inaktiv' }}
                    </span>
                  </td>
                  <td>
                    <button @click="editPartner(partner)" class="action-button edit">Bearbeiten</button>
                    <button @click="togglePartnerStatus(partner)" class="action-button toggle">
                      {{ partner.is_active ? 'Deaktivieren' : 'Aktivieren' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Users Tab -->
        <div v-if="activeTab === 'users'" class="tab-content">
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Partner</th>
                  <th>Status</th>
                  <th>Aktionen</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in partnerUsers" :key="user.id">
                  <td>{{ user.id }}</td>
                  <td>{{ user.name }}</td>
                  <td>{{ user.email }}</td>
                  <td>{{ user.partner_name }}</td>
                  <td>
                    <span :class="['status-badge', user.is_active ? 'status-active' : 'status-inactive']">
                      {{ user.is_active ? 'Aktiv' : 'Inaktiv' }}
                    </span>
                  </td>
                  <td>
                    <button @click="editUser(user)" class="action-button edit">Bearbeiten</button>
                    <button @click="toggleUserStatus(user)" class="action-button toggle">
                      {{ user.is_active ? 'Deaktivieren' : 'Aktivieren' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Payments Tab -->
        <div v-if="activeTab === 'payments'" class="tab-content">
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Partner</th>
                  <th>Betrag</th>
                  <th>Status</th>
                  <th>Datum</th>
                  <th>Aktionen</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="payment in partnerPayments" :key="payment.id">
                  <td>{{ payment.id }}</td>
                  <td>{{ payment.partner_name }}</td>
                  <td>{{ payment.amount }} USDT</td>
                  <td>
                    <span :class="['status-badge', payment.status === 'completed' ? 'status-active' : 'status-inactive']">
                      {{ payment.status }}
                    </span>
                  </td>
                  <td>{{ formatDate(payment.created_at) }}</td>
                  <td>
                    <button @click="editPayment(payment)" class="action-button edit">Bearbeiten</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Add Partner Modal -->
        <div v-if="showAddPartnerModal" class="modal-overlay" @click="showAddPartnerModal = false">
          <div class="modal-content" @click.stop>
            <h2 class="modal-title">Partner hinzufügen</h2>
            <form @submit.prevent="addPartner" class="modal-form">
              <div class="form-group">
                <label for="name" class="form-label">Name</label>
                <input
                  id="name"
                  v-model="newPartner.name" 
                  type="text"
                  required
                  class="form-input"
                />
              </div>
              
              <div class="form-group">
                <label for="email" class="form-label">Email</label>
                <input
                  id="email"
                  v-model="newPartner.email" 
                  type="email" 
                  required
                  class="form-input"
                />
              </div>
              
              <div class="form-group">
                <label for="telegram" class="form-label">Telegram ID</label>
                <input
                  id="telegram"
                  v-model="newPartner.telegram_id" 
                  type="text"
                  class="form-input"
                />
              </div>
              
              <div class="form-group">
                <label class="form-label">Status</label>
                <div class="checkbox-group">
                  <label class="checkbox-label">
                    <input
                      type="checkbox"
                      v-model="newPartner.is_active"
                      class="checkbox-input"
                    />
                    Aktiv
                  </label>
                </div>
              </div>
              
              <div class="modal-actions">
                <button type="button" @click="showAddPartnerModal = false" class="cancel-button">
                  Abbrechen
                </button>
                <button type="submit" class="submit-button">
                  Hinzufügen
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Edit Partner Modal -->
        <div v-if="showEditPartnerModal" class="modal-overlay" @click="showEditPartnerModal = false">
          <div class="modal-content" @click.stop>
            <h2 class="modal-title">Partner bearbeiten</h2>
            <form @submit.prevent="updatePartner" class="modal-form">
              <div class="form-group">
                <label for="edit-name" class="form-label">Name</label>
                <input
                  id="edit-name"
                  v-model="editingPartner.name" 
                  type="text"
                  required
                  class="form-input"
                />
              </div>
              
              <div class="form-group">
                <label for="edit-email" class="form-label">Email</label>
                <input 
                  id="edit-email"
                  v-model="editingPartner.email" 
                  type="email" 
                  required
                  class="form-input"
                />
              </div>
              
              <div class="form-group">
                <label for="edit-telegram" class="form-label">Telegram ID</label>
                <input
                  id="edit-telegram"
                  v-model="editingPartner.telegram_id" 
                  type="text"
                  class="form-input"
                />
              </div>
              
              <div class="form-group">
                <label class="form-label">Status</label>
                <div class="checkbox-group">
                  <label class="checkbox-label">
                    <input 
                      type="checkbox" 
                      v-model="editingPartner.is_active"
                      class="checkbox-input"
                    />
                    Aktiv
                  </label>
                </div>
              </div>

              <div class="modal-actions">
                <button type="button" @click="showEditPartnerModal = false" class="cancel-button">
                  Abbrechen
                </button>
                <button type="submit" class="submit-button">
                  Speichern
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

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useToast } from 'vue-toastification'

const toast = useToast()
const isSuperAdmin = ref(false)
const partners = ref([])
const signalGroups = ref([])
const payments = ref([])
const selectedPaymentType = ref('')

const showCreatePartnerModal = ref(false)
const showEditPartnerModal = ref(false)
const showCreateSignalGroupModal = ref(false)
const showEditSignalGroupModal = ref(false)
const showEditPaymentModal = ref(false)

const currentPartner = ref({
  telegram_id: '',
  phone: '',
  permissions: {
    can_manage_users: false,
    can_manage_packages: false,
    can_manage_payments: false,
    can_manage_signal_groups: false,
    can_view_statistics: false,
    can_manage_features: false
  }
})

const currentSignalGroup = ref({
  name: '',
  description: '',
  price: 0,
  partner_id: null
})

const currentPayment = ref({
  status: ''
})

onMounted(async () => {
  await checkUserRole()
  await loadPartners()
  await loadSignalGroups()
  await loadPayments()
})

const checkUserRole = async () => {
  try {
    const response = await axios.get('/api/admin/me')
    isSuperAdmin.value = response.data.role === 'SUPERADMIN'
  } catch (error) {
    console.error('Fehler beim Laden der Benutzerrolle:', error)
  }
}

const loadPartners = async () => {
  if (!isSuperAdmin.value) return
  try {
    const response = await axios.get('/api/admin/partners')
    partners.value = response.data
  } catch (error) {
    console.error('Fehler beim Laden der Partner:', error)
    toast.error('Fehler beim Laden der Partner')
  }
}

const loadSignalGroups = async () => {
  try {
    const response = await axios.get('/api/admin/signal-groups')
    signalGroups.value = response.data
  } catch (error) {
    console.error('Fehler beim Laden der Signal-Gruppen:', error)
    toast.error('Fehler beim Laden der Signal-Gruppen')
  }
}

const loadPayments = async () => {
  try {
    const response = await axios.get('/api/admin/payments', {
      params: { payment_type: selectedPaymentType.value || undefined }
    })
    payments.value = response.data
  } catch (error) {
    console.error('Fehler beim Laden der Zahlungen:', error)
    toast.error('Fehler beim Laden der Zahlungen')
  }
}

const editPartner = async (partner) => {
  try {
    const response = await axios.get(`/api/admin/partners/${partner.id}/permissions`)
    currentPartner.value = {
      ...partner,
      permissions: response.data
    }
    showEditPartnerModal.value = true
  } catch (error) {
    console.error('Fehler beim Laden der Partner-Berechtigungen:', error)
    toast.error('Fehler beim Laden der Partner-Berechtigungen')
  }
}

const editSignalGroup = (group) => {
  currentSignalGroup.value = { ...group }
  showEditSignalGroupModal.value = true
}

const editPayment = (payment) => {
  currentPayment.value = { ...payment }
  showEditPaymentModal.value = true
}

const savePartner = async () => {
  try {
    if (showEditPartnerModal.value) {
      await axios.put(`/api/admin/partners/${currentPartner.value.id}`, currentPartner.value)
      toast.success('Partner erfolgreich aktualisiert')
    } else {
      await axios.post('/api/admin/partners', currentPartner.value)
      toast.success('Partner erfolgreich erstellt')
    }
    showCreatePartnerModal.value = false
    showEditPartnerModal.value = false
    await loadPartners()
  } catch (error) {
    console.error('Fehler beim Speichern des Partners:', error)
    toast.error('Fehler beim Speichern des Partners')
  }
}

const saveSignalGroup = async () => {
  try {
    if (showEditSignalGroupModal.value) {
      await axios.put(`/api/admin/signal-groups/${currentSignalGroup.value.id}`, currentSignalGroup.value)
      toast.success('Signal-Gruppe erfolgreich aktualisiert')
    } else {
      await axios.post('/api/admin/signal-groups', currentSignalGroup.value)
      toast.success('Signal-Gruppe erfolgreich erstellt')
    }
    showCreateSignalGroupModal.value = false
    showEditSignalGroupModal.value = false
    await loadSignalGroups()
  } catch (error) {
    console.error('Fehler beim Speichern der Signal-Gruppe:', error)
    toast.error('Fehler beim Speichern der Signal-Gruppe')
  }
}

const savePayment = async () => {
  try {
    await axios.put(`/api/admin/payments/${currentPayment.value.id}`, currentPayment.value)
    toast.success('Zahlung erfolgreich aktualisiert')
    showEditPaymentModal.value = false
    await loadPayments()
  } catch (error) {
    console.error('Fehler beim Speichern der Zahlung:', error)
    toast.error('Fehler beim Speichern der Zahlung')
  }
}

const getStatusClass = (status) => {
  switch (status) {
    case 'COMPLETED':
      return 'bg-green-100 text-green-800'
    case 'PENDING':
      return 'bg-yellow-100 text-yellow-800'
    case 'FAILED':
      return 'bg-red-100 text-red-800'
    case 'REFUNDED':
      return 'bg-gray-100 text-gray-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}
</script> 

<!-- Styles werden aus globaler index.css verwendet --> 