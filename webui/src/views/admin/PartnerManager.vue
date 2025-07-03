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
        <h1 class="text-2xl font-bold">Partner verwalten</h1>
      </div>
      
      <button
        @click="showCreateModal = true"
        class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors"
      >
        Neuen Partner erstellen
      </button>
    </div>

    <!-- Partner-Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="partner in partners" :key="partner.id" class="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="font-medium text-gray-900">{{ partner.display_name }}</h3>
            <p class="text-sm text-gray-500">{{ partner.name }}</p>
          </div>
          <span :class="['px-2 py-1 rounded-full text-xs', partner.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800']">
            {{ partner.is_active ? 'Aktiv' : 'Inaktiv' }}
          </span>
        </div>
        
        <p class="text-sm text-gray-600 mb-4">{{ partner.description }}</p>
        
        <div class="text-sm text-gray-500 mb-4">
          <div>API Key: <code class="bg-gray-100 px-1 rounded">{{ partner.api_key }}</code></div>
          <div>Webhook URL: <code class="bg-gray-100 px-1 rounded">{{ partner.webhook_url || 'Nicht gesetzt' }}</code></div>
        </div>

        <div class="mb-4">
          <h4 class="font-medium text-sm mb-2">Berechtigungen:</h4>
          <div class="space-y-1">
            <div v-for="(enabled, permission) in partner.permissions" :key="permission" class="text-xs">
              <span :class="enabled ? 'text-green-600' : 'text-gray-400'">
                {{ enabled ? '✅' : '❌' }} {{ getPermissionName(permission) }}
              </span>
            </div>
          </div>
        </div>

        <div class="flex space-x-2">
          <button
            @click="editPartner(partner)"
            class="text-blue-600 hover:text-blue-900 text-sm transition-colors"
          >
            Bearbeiten
          </button>
          <button
            @click="deletePartner(partner)"
            class="text-red-600 hover:text-red-900 text-sm transition-colors"
          >
            Löschen
          </button>
        </div>
      </div>
    </div>

    <!-- Partner Tabelle -->
    <div v-if="isSuperAdmin" class="mb-8">
      <h2 class="text-xl font-semibold mb-4">Partner</h2>
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Telegram ID
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Telefon
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Aktionen
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="partner in partners" :key="partner.id">
              <td class="px-6 py-4 whitespace-nowrap">{{ partner.telegram_id }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ partner.phone }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'px-2 py-1 text-xs rounded-full',
                    partner.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  ]"
                >
                  {{ partner.is_active ? 'Aktiv' : 'Inaktiv' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <button
                  @click="editPartner(partner)"
                  class="text-blue-600 hover:text-blue-900 mr-3"
                >
                  Bearbeiten
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Signal-Gruppen Tabelle -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-4">Signal-Gruppen</h2>
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Name
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Beschreibung
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Preis
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Aktionen
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="group in signalGroups" :key="group.id">
              <td class="px-6 py-4 whitespace-nowrap">{{ group.name }}</td>
              <td class="px-6 py-4">{{ group.description }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ group.price }} BUSD</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'px-2 py-1 text-xs rounded-full',
                    group.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  ]"
                >
                  {{ group.is_active ? 'Aktiv' : 'Inaktiv' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <button
                  @click="editSignalGroup(group)"
                  class="text-blue-600 hover:text-blue-900"
                >
                  Bearbeiten
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Zahlungen Tabelle -->
    <div>
      <h2 class="text-xl font-semibold mb-4">Zahlungen</h2>
      <div class="mb-4">
        <select
          v-model="selectedPaymentType"
          class="border rounded px-3 py-2"
          @change="loadPayments"
        >
          <option value="">Alle Zahlungen</option>
          <option value="SIGNAL_GROUP">Signal-Gruppen</option>
          <option value="PACKAGE">Pakete</option>
        </select>
      </div>
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Benutzer
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Betrag
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Typ
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Datum
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Aktionen
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="payment in payments" :key="payment.id">
              <td class="px-6 py-4 whitespace-nowrap">{{ payment.user.telegram_id }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ payment.amount }} {{ payment.currency }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ payment.payment_type }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'px-2 py-1 text-xs rounded-full',
                    getStatusClass(payment.status)
                  ]"
                >
                  {{ payment.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                {{ new Date(payment.created_at).toLocaleDateString() }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <button
                  v-if="isSuperAdmin"
                  @click="editPayment(payment)"
                  class="text-blue-600 hover:text-blue-900"
                >
                  Bearbeiten
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Partner Modal -->
    <div v-if="showCreatePartnerModal || showEditPartnerModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold mb-4">
          {{ showEditPartnerModal ? 'Partner bearbeiten' : 'Neuer Partner' }}
        </h3>
        <form @submit.prevent="savePartner">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700">Telegram ID</label>
            <input
              v-model="currentPartner.telegram_id"
              type="text"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            />
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700">Telefon</label>
            <input
              v-model="currentPartner.phone"
              type="text"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            />
          </div>
          <div class="mb-4">
            <h4 class="text-sm font-medium text-gray-700 mb-2">Berechtigungen</h4>
            <div class="space-y-2">
              <label class="flex items-center">
                <input
                  v-model="currentPartner.permissions.can_manage_users"
                  type="checkbox"
                  class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
                <span class="ml-2 text-sm text-gray-600">Benutzer verwalten</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="currentPartner.permissions.can_manage_packages"
                  type="checkbox"
                  class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
                <span class="ml-2 text-sm text-gray-600">Pakete verwalten</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="currentPartner.permissions.can_manage_payments"
                  type="checkbox"
                  class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
                <span class="ml-2 text-sm text-gray-600">Zahlungen verwalten</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="currentPartner.permissions.can_manage_signal_groups"
                  type="checkbox"
                  class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
                <span class="ml-2 text-sm text-gray-600">Signal-Gruppen verwalten</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="currentPartner.permissions.can_view_statistics"
                  type="checkbox"
                  class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
                <span class="ml-2 text-sm text-gray-600">Statistiken einsehen</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="currentPartner.permissions.can_manage_features"
                  type="checkbox"
                  class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
                <span class="ml-2 text-sm text-gray-600">Funktionen verwalten</span>
              </label>
            </div>
          </div>
          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="showCreatePartnerModal = false; showEditPartnerModal = false"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
            >
              Abbrechen
            </button>
            <button
              type="submit"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-500 rounded-md hover:bg-blue-600"
            >
              Speichern
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Signal-Gruppe Modal -->
    <div v-if="showCreateSignalGroupModal || showEditSignalGroupModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold mb-4">
          {{ showEditSignalGroupModal ? 'Signal-Gruppe bearbeiten' : 'Neue Signal-Gruppe' }}
        </h3>
        <form @submit.prevent="saveSignalGroup">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700">Name</label>
            <input
              v-model="currentSignalGroup.name"
              type="text"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            />
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700">Beschreibung</label>
            <textarea
              v-model="currentSignalGroup.description"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              rows="3"
              required
            ></textarea>
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700">Preis (BUSD)</label>
            <input
              v-model="currentSignalGroup.price"
              type="number"
              step="0.01"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            />
          </div>
          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="showCreateSignalGroupModal = false; showEditSignalGroupModal = false"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
            >
              Abbrechen
            </button>
            <button
              type="submit"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-500 rounded-md hover:bg-blue-600"
            >
              Speichern
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Zahlung Modal -->
    <div v-if="showEditPaymentModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold mb-4">Zahlung bearbeiten</h3>
        <form @submit.prevent="savePayment">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700">Status</label>
            <select
              v-model="currentPayment.status"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            >
              <option value="PENDING">Ausstehend</option>
              <option value="COMPLETED">Abgeschlossen</option>
              <option value="FAILED">Fehlgeschlagen</option>
              <option value="REFUNDED">Rückerstattet</option>
            </select>
          </div>
          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="showEditPaymentModal = false"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
            >
              Abbrechen
            </button>
            <button
              type="submit"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-500 rounded-md hover:bg-blue-600"
            >
              Speichern
            </button>
          </div>
        </form>
      </div>
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