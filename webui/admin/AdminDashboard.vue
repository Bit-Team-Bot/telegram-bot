<template>
  <div class="admin-dashboard">
    <h1>Admin-Dashboard</h1>

    <section>
      <h2>Offene Zahlungen</h2>
      <table class="payments-table">
        <thead>
          <tr>
            <th>User ID</th>
            <th>Payment ID</th>
            <th>Paket</th>
            <th>Betrag</th>
            <th>Datum</th>
            <th>Aktion</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in pendingPayments" :key="p.payment_id">
            <td>{{ p.user_id }}</td>
            <td>{{ p.payment_id }}</td>
            <td>{{ getPackageName(p.package_id) }}</td>
            <td>{{ p.amount }} USDT</td>
            <td>{{ p.created_at }}</td>
            <td>
              <button @click="setPaid(p.payment_id)">Auf bezahlt setzen</button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <section>
      <h2>Alle User</h2>
      <table class="users-table">
        <thead>
          <tr>
            <th>User ID</th>
            <th>Phone</th>
            <th>Superadmin</th>
            <th>Pakete</th>
            <th>Aktionen</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td>{{ u.id }}</td>
            <td>{{ u.phone }}</td>
            <td>{{ u.is_superadmin ? 'Ja' : 'Nein' }}</td>
            <td>{{ u.package_id }}</td>
            <td>
              <!-- Aktionen: Erweiterbar -->
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <section>
      <h2>Pakete</h2>
      <ul>
        <li v-for="pkg in packages" :key="pkg.id">
          {{ pkg.name }} ({{ pkg.duration_days > 0 ? pkg.duration_days + ' Tage' : 'Lifetime' }}) — {{ pkg.price_usdt }} USDT
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../src/stores/auth'
import api from '../src/api'

const authStore = useAuthStore()
const pendingPayments = ref([])
const users = ref([])
const packages = ref([])

const fetchPendingPayments = async () => {
  try {
    const res = await api.get('/admin/pending_payments')
    pendingPayments.value = res.data
  } catch (error) {
    alert('Fehler beim Laden der Zahlungen: ' + (error.response?.data?.detail || error.message))
  }
}
const fetchUsers = async () => {
  try {
    const res = await api.get('/admin/all_users')
    users.value = res.data
  } catch (error) {
    alert('Fehler beim Laden der User: ' + (error.response?.data?.detail || error.message))
  }
}
const fetchPackages = async () => {
  try {
    const res = await api.get('/packages/')
    packages.value = res.data
  } catch (error) {
    alert('Fehler beim Laden der Pakete: ' + (error.response?.data?.detail || error.message))
  }
}

const getPackageName = (id) => {
  const pkg = packages.value.find(p => p.id == id)
  return pkg ? pkg.name : 'Unbekannt'
}

const setPaid = async (paymentId) => {
  try {
    const res = await api.post('/admin/confirm_payment', { payment_id: paymentId })
    alert("Zahlung als bezahlt markiert!")
    fetchPendingPayments()
  } catch (error) {
    alert("Fehler: " + (error.response?.data?.detail || error.message))
  }
}

onMounted(() => {
  if (!authStore.isSuperadmin) {
    alert("Kein Admin-Zugang!")
    window.location = "/dashboard"
    return
  }
  fetchPendingPayments()
  fetchUsers()
  fetchPackages()
})
</script>

<style scoped>
.admin-dashboard {
  max-width: 1000px;
  margin: 32px auto;
  color: #fff;
}
.payments-table, .users-table {
  width: 100%;
  margin-bottom: 24px;
  background: #23263b;
  border-radius: 12px;
  overflow: hidden;
}
.payments-table th, .payments-table td,
.users-table th, .users-table td {
  padding: 8px 13px;
  border-bottom: 1px solid #2b3147;
}
.payments-table th, .users-table th {
  background: #191b23;
}
button {
  background: #ffb32b;
  color: #222;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  padding: 8px 20px;
  cursor: pointer;
}
</style>
