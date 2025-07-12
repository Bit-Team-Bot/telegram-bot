<template>
  <div class="dashboard-container">
    <!-- Header über die ganze Breite -->
    <div class="header-section">
      <img src="@/assets/wallstreet-header.png" alt="Wallstreet Crypto Header" class="header-image" />
    </div>

    <!-- User Role Box 1: Admin/Partner + Logout + Paketstatus/Zahlungen -->
    <div class="user-role-box">
      <div class="role-content">
        <div class="role-section">
          <template v-if="authStore.isSuperadmin">
            <div style="display: flex; flex-direction: column; gap: 8px;">
              <button @click="goAdmin" class="role-btn admin">
                <span class="role-icon">👑</span>
                <span class="role-text">Administrator</span>
              </button>
              <button @click="goPartner" class="role-btn admin">
                <span class="role-icon">🤝</span>
                <span class="role-text">Partner</span>
              </button>
            </div>
          </template>
          <template v-if="authStore.isPartner">
            <button @click="goPartner" class="role-btn admin">
              <span class="role-icon">🤝</span>
              <span class="role-text">Partner</span>
            </button>
          </template>
          
          <!-- Logout Button direkt neben dem Role Button -->
          <button @click="logout" class="logout-btn">
            <span class="logout-icon">🚪</span>
            <span class="logout-text">Logout</span>
          </button>
        </div>
        
        <!-- Paketstatus und Zahlungen nebeneinander -->
        <div class="status-payments-row">
          <!-- Paketstatus und verbleibende Tage -->
          <div class="package-status-section">
            <div class="status-item">
              <span class="status-label">Paket:</span>
              <span class="status-value">{{ packageStatus.packageName || 'Kein Paket' }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">Status:</span>
              <span class="status-value" :class="{ 'active': packageStatus.isActive, 'inactive': !packageStatus.isActive }">
                {{ packageStatus.isActive ? 'Aktiv' : 'Inaktiv' }}
              </span>
            </div>
            <div v-if="packageStatus.remainingDays !== null" class="status-item">
              <span class="status-label">Verbleibend:</span>
              <span class="status-value">{{ packageStatus.remainingDays }} Tage</span>
            </div>
          </div>
          
          <!-- Zahlungen -->
          <div class="payments-section">
            <div class="payments-header">
              <span class="payments-icon">💰</span>
              <span class="payments-text">Zahlungen</span>
            </div>
            <div class="payments-count">
              {{ paymentsCount }} Zahlungen
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- User Role Box 2: Hauptnavigation (Pakete, Gruppen, Signalgruppen) -->
    <div class="user-role-box">
      <div class="role-content">
        <div class="status-payments-row">
          <router-link to="/packages" class="nav-card">
            <div class="card-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="currentColor"/>
              </svg>
            </div>
            <h3 class="card-title">Pakete</h3>
            <p class="card-description">Verfügbare Abonnements</p>
          </router-link>

          <router-link to="/groups" class="nav-card">
            <div class="card-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M16 4C16 2.89 15.11 2 14 2C12.89 2 12 2.89 12 4C12 5.11 12.89 6 14 6C15.11 6 16 5.11 16 4M20 22V16H16.5L15.56 15H8.44L7.5 16H4V22H20M22 22H2V16C2 14.89 2.89 14 4 14H7L8 12H16L17 14H20C21.11 14 22 14.89 22 16V22M10 4C10 2.89 9.11 2 8 2C6.89 2 6 2.89 6 4C6 5.11 6.89 6 8 6C9.11 6 10 5.11 10 4Z" fill="currentColor"/>
              </svg>
            </div>
            <h3 class="card-title">Gruppen</h3>
            <p class="card-description">Telegram Gruppen verwalten</p>
          </router-link>
        </div>
        
        <div class="status-payments-row">
          <router-link to="/signal-groups" class="nav-card" style="flex: 1;">
            <div class="card-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M16 4C16 2.89 15.11 2 14 2C12.89 2 12 2.89 12 4C12 5.11 12.89 6 14 6C15.11 6 16 5.11 16 4M20 22V16H16.5L15.56 15H8.44L7.5 16H4V22H20M22 22H2V16C2 14.89 2.89 14 4 14H7L8 12H16L17 14H20C21.11 14 22 14.89 22 16V22M10 4C10 2.89 9.11 2 8 2C6.89 2 6 2.89 6 4C6 5.11 6.89 6 8 6C9.11 6 10 5.11 10 4Z" fill="currentColor"/>
              </svg>
            </div>
            <h3 class="card-title">Signalgruppen</h3>
            <p class="card-description">Trading Signale</p>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router = useRouter()
const authStore = useAuthStore()

// Reaktive Daten für Paketstatus und Zahlungen
const packageStatus = ref({
  packageName: null,
  isActive: false,
  remainingDays: null
})
const paymentsCount = ref(0)

const logout = () => {
  authStore.logout()
  router.push('/login')
}

const goAdmin = () => {
  router.push('/admin-dashboard')
}

const goPartner = () => {
  router.push('/partner-dashboard')
}

// Laden der Paketstatus-Daten
const loadPackageStatus = async () => {
  try {
    // Aktuelles Paket abrufen
    const packageResponse = await api.get('/user/packages/current')
    const packageData = packageResponse.data
    
    if (packageData.has_package && packageData.package) {
      const packageInfo = packageData.package
      const template = packageData.template
      
      packageStatus.value.packageName = template?.display_name || packageInfo.name
      packageStatus.value.isActive = packageInfo.status === 'active'
      
      // Verbleibende Tage berechnen
      if (packageInfo.end_date) {
        const endDate = new Date(packageInfo.end_date)
        const now = new Date()
        const diffTime = endDate.getTime() - now.getTime()
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
        packageStatus.value.remainingDays = diffDays > 0 ? diffDays : 0
      } else if (packageInfo.duration_days === 0) {
        packageStatus.value.remainingDays = null // Lifetime
      } else {
        packageStatus.value.remainingDays = 0
      }
    } else {
      packageStatus.value = {
        packageName: null,
        isActive: false,
        remainingDays: null
      }
    }
  } catch (error) {
    console.error('Fehler beim Laden des Paketstatus:', error)
    packageStatus.value = {
      packageName: null,
      isActive: false,
      remainingDays: null
    }
  }
}

// Laden der Zahlungsdaten
const loadPaymentsCount = async () => {
  try {
    const paymentsResponse = await api.get('/payments/user/' + authStore.userId)
    paymentsCount.value = paymentsResponse.data.length
  } catch (error) {
    console.error('Fehler beim Laden der Zahlungen:', error)
    paymentsCount.value = 0
  }
}

// Daten beim Mounten laden
onMounted(async () => {
  await Promise.all([
    loadPackageStatus(),
    loadPaymentsCount()
  ])
})
</script>

<!-- TODO: Menüstruktur wie oben beschrieben umbauen. -->
<!-- TODO: Admin-Bereich nur noch nach Klick anzeigen, nicht mehr im Menü. -->
<!-- TODO: Einheitliche Styles für alle Boxen und Buttons laut globaler Klasse verwenden. -->
<!-- TODO: Überprüfe lokale Style-Blöcke in Komponenten und räume sie ggf. auf. -->
