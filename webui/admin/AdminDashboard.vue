<template>
  <div class="dashboard-container">
    <div class="header-section">
      <img src="@/assets/wallstreet-header.png" alt="Wallstreet Crypto Header" class="header-image" />

    </div>
    <div class="main-content">
      <BaseCard style="flex-direction:column;align-items:center;width:100%;max-width:1100px;">
        <div class="welcome-section">
          <h2 class="welcome-title">Admin-Dashboard</h2>
          <p class="welcome-subtitle">Verwalten Sie Benutzer, Zahlungen und Pakete</p>
        </div>
        <div class="dashboard-sections-grid">
          <BaseCard>
            <h3 class="section-title">Offene Zahlungen</h3>
            <ul>
              <li v-for="p in pendingPayments" :key="p.id">
                <span style="color:var(--bt-orange);font-weight:600;">{{ p.user_id }}</span> | {{ p.amount }} USDT | {{ p.created_at }}
                <BaseButton @click="setPaid(p.id)" style="margin-left:10px;">Bezahlt</BaseButton>
              </li>
            </ul>
          </BaseCard>
          <BaseCard>
            <h3 class="section-title">Benutzer</h3>
            <ul>
              <li v-for="u in users.slice(0,5)" :key="u.id">
                <span style="color:var(--bt-orange);font-weight:600;">{{ u.phone }}</span> | {{ u.is_superadmin ? 'Admin' : 'User' }}
              </li>
            </ul>
            <router-link to="/admin/users"><BaseButton style="margin-top:10px;">Alle Benutzer</BaseButton></router-link>
          </BaseCard>
          <BaseCard>
            <h3 class="section-title">Pakete</h3>
            <ul>
              <li v-for="pkg in packages.slice(0,5)" :key="pkg.id">
                <span style="color:var(--bt-orange);font-weight:600;">{{ pkg.name }}</span> | {{ pkg.price_usdt }} USDT
              </li>
            </ul>
            <router-link to="/admin/packages"><BaseButton style="margin-top:10px;">Alle Pakete</BaseButton></router-link>
          </BaseCard>
        </div>
        <div class="back-section">
          <BaseButton @click="$router.push('/dashboard')">
  Zurück zum Dashboard
</BaseButton>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../src/stores/auth'
import BaseCard from '../src/components/BaseCard.vue'
import BaseButton from '../src/components/BaseButton.vue'
import api from '../src/api'

const authStore = useAuthStore()
const pendingPayments = ref([])
const users = ref([])
const packages = ref([])

const fetchPendingPayments = async () => {
  try {
    const res = await api.get('/payments/pending')
    pendingPayments.value = res.data
  } catch (error) {
    console.error('Fehler beim Laden der Zahlungen:', error)
    let msg = error.response?.data?.detail || error.message
    if (typeof msg === 'object') msg = JSON.stringify(msg)
    alert('Fehler beim Laden der Zahlungen: ' + msg)
  }
}
const fetchUsers = async () => {
  try {
    const res = await api.get('/admin/users')
    users.value = res.data
  } catch (error) {
    alert('Fehler beim Laden der User: ' + (error.response?.data?.detail || error.message))
  }
}
const fetchPackages = async () => {
  try {
    const res = await api.get('/admin/packages')
    packages.value = res.data
  } catch (error) {
    alert('Fehler beim Laden der Pakete: ' + (error.response?.data?.detail || error.message))
  }
}

const setPaid = async (paymentId) => {
  try {
    await api.post(`/admin/payments/${paymentId}/confirm`)
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
.dashboard-container {
  min-height: 100vh;
  background: var(--bt-bg-dark);
  display: flex;
  flex-direction: column;
  align-items: center;
  color: white;
}
/* Header-Section Styles werden von der globalen index.css übernommen */
/* Header-Bild Styles werden von der globalen index.css übernommen */
.header-text {
  text-align: center;
}
.admin-badge {
  display: inline-flex;
  align-items: center;
  background: linear-gradient(135deg, #FFA726 0%, #FF9800 100%);
  color: #000000;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
  margin-top: 8px;
  box-shadow: 0 4px 15px rgba(255, 167, 38, 0.3);
}
.admin-icon {
  margin-right: 6px;
  font-size: 1.1rem;
}
.admin-text {
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.main-content {
  width: 100%;
  max-width: 1200px;
  padding: 0 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.welcome-section {
  text-align: center;
  margin-bottom: 32px;
}
.welcome-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 12px 0;
}
.welcome-subtitle {
  font-size: 1.1rem;
  color: #CCCCCC;
  margin: 0;
  font-weight: 300;
}
.dashboard-sections-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  width: 100%;
  margin-bottom: 48px;
}
.section-title {
  color: var(--bt-orange);
  font-size: 1.3rem;
  font-weight: 700;
  margin-bottom: 10px;
}
/* Back-Section Styles werden von der globalen index.css übernommen */
</style>
