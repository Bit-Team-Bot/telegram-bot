<template>
  <div class="dashboard-container">
    <div class="header-section">
      <img src="@/assets/wallstreet-header.png" alt="Wallstreet Crypto Header" class="header-image" />

    </div>
    <div class="main-content">
      <BaseCard style="flex-direction:column;align-items:center;width:100%;max-width:1100px;">
        <div class="welcome-section">
          <h2 class="welcome-title">Partner-Dashboard</h2>
          <p class="welcome-subtitle">Ihre Gruppen, Partner-Links und Provisionen</p>
        </div>
        <div class="dashboard-sections-grid">
          <BaseCard>
            <h3 class="section-title">Meine Gruppen</h3>
            <ul>
              <li v-for="g in partnerGroups" :key="g.id">
                <span style="color:var(--bt-orange);font-weight:600;">{{ g.name }}</span> ({{ g.member_count }} Mitglieder)
              </li>
            </ul>
          </BaseCard>
          <BaseCard>
            <h3 class="section-title">Partner-Links</h3>
            <ul>
              <li v-for="l in partnerLinks" :key="l.id">
                <a :href="l.url" target="_blank" style="color:var(--bt-orange);text-decoration:underline;">{{ l.url }}</a>
              </li>
            </ul>
          </BaseCard>
          <BaseCard>
            <h3 class="section-title">Provisionen</h3>
            <ul>
              <li v-for="c in commissions" :key="c.id">
                {{ c.amount }} USDT am {{ c.date }}
              </li>
            </ul>
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
import api from '../../api'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const partnerGroups = ref([])
const partnerLinks = ref([])
const commissions = ref([])

const fetchPartnerGroups = async () => {
  try {
    const res = await api.get('/partner/groups')
    partnerGroups.value = res.data
  } catch (error) {
    alert('Fehler beim Laden der Gruppen: ' + (error.response?.data?.detail || error.message))
  }
}
const fetchPartnerLinks = async () => {
  try {
    const res = await api.get('/partner/links')
    partnerLinks.value = res.data
  } catch (error) {
    alert('Fehler beim Laden der Links: ' + (error.response?.data?.detail || error.message))
  }
}
const fetchCommissions = async () => {
  try {
    const res = await api.get('/partner/commissions')
    commissions.value = res.data
  } catch (error) {
    alert('Fehler beim Laden der Provisionen: ' + (error.response?.data?.detail || error.message))
  }
}

onMounted(() => {
  if (!authStore.isPartner) {
    alert('Kein Partner-Zugang!')
    window.location = '/dashboard'
    return
  }
  fetchPartnerGroups()
  fetchPartnerLinks()
  fetchCommissions()
})
</script>

<!-- Styles werden aus globaler index.css verwendet --> 