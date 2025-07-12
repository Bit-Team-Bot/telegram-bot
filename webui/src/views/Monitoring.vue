<template>
  <div class="monitoring-container">
    <main class="monitoring-content">
      <div v-if="!isAllowed" class="no-access">
        <h2>Kein Zugriff</h2>
        <p>Diese Seite ist nur für Administratoren und Partner sichtbar.</p>
      </div>
      <template v-else>
      <div class="page-header">
        <h1 class="page-title">System-Monitoring</h1>
        <p class="page-subtitle">Überwachung von Performance und System-Ressourcen</p>
      </div>

      <!-- Status-Übersicht -->
      <div class="status-overview">
        <BaseCard :class="overallStatus">
          <div class="status-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="currentColor"/>
            </svg>
          </div>
          <div class="status-content">
            <h3 class="status-title">Gesamtstatus</h3>
            <p class="status-value">{{ overallStatusText }}</p>
          </div>
        </BaseCard>
      </div>

      <!-- Performance-Metriken -->
      <div class="metrics-section">
        <h2 class="section-title">Performance (letzte 24h)</h2>
        <div class="metrics-grid">
          <BaseCard v-for="(metric, idx) in metricsList" :key="idx">
            <div class="metric-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M13 2.05V4.05C17.39 4.59 20.5 8.58 19.96 12.97C19.5 16.61 16.64 19.5 13 19.93V21.93C18.5 21.38 22.5 16.5 21.95 11C21.5 6.25 17.73 2.5 13 2.03V2.05M5.67 19.74C7.18 21 9.04 21.79 11 22V20C9.58 19.82 8.23 19.25 7.1 18.37L5.67 19.74M7.1 5.74C8.22 4.84 9.57 4.26 11 4.06V2.06C9.05 2.25 7.19 3 5.67 4.26L7.1 5.74M5.69 7.1L4.26 5.67C3 7.19 2.25 9.04 2.05 11H4.05C4.24 9.58 4.8 8.23 5.69 7.1M4.06 13H2.06C2.26 14.96 3.03 16.81 4.27 18.33L5.69 16.9C4.81 15.77 4.24 14.42 4.06 13M10 16.5L16 14L13 15.5V7.5L7 10L10 8.5V16.5Z" fill="var(--accent-orange)"/>
              </svg>
            </div>
            <div class="metric-content">
              <h3 class="metric-title">{{ metric.title }}</h3>
              <p class="metric-value">{{ metric.value }}</p>
            </div>
          </BaseCard>
        </div>
      </div>

      <!-- System-Ressourcen -->
      <div class="metrics-section">
        <h2 class="section-title">System-Ressourcen</h2>
        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="var(--accent-orange)"/>
              </svg>
            </div>
            <div class="metric-content">
              <h3 class="metric-title">CPU-Auslastung</h3>
              <p class="metric-value">{{ system.current_cpu || 0 }}%</p>
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="var(--accent-orange)"/>
              </svg>
            </div>
            <div class="metric-content">
              <h3 class="metric-title">RAM-Auslastung</h3>
              <p class="metric-value">{{ system.current_memory || 0 }}%</p>
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="var(--accent-orange)"/>
              </svg>
            </div>
            <div class="metric-content">
              <h3 class="metric-title">Festplatten-Auslastung</h3>
              <p class="metric-value">{{ system.current_disk || 0 }}%</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Top-Endpoints -->
      <div class="metrics-section" v-if="performance.top_endpoints && performance.top_endpoints.length > 0">
        <h2 class="section-title">Top-Endpoints</h2>
        <div class="endpoints-list">
          <div v-for="(endpoint, index) in performance.top_endpoints" :key="index" class="endpoint-item">
            <span class="endpoint-name">{{ endpoint[0] }}</span>
            <span class="endpoint-count">{{ endpoint[1] }} Requests</span>
          </div>
        </div>
      </div>

      <!-- Fehler-Logs -->
      <div class="metrics-section" v-if="errors.errors && errors.errors.length > 0">
        <h2 class="section-title">Neueste Fehler</h2>
        <div class="errors-list">
          <div v-for="error in errors.errors" :key="error.timestamp" class="error-item">
            <div class="error-header">
              <span class="error-type">{{ error.error_type }}</span>
              <span class="error-time">{{ formatTime(error.timestamp) }}</span>
            </div>
            <p class="error-message">{{ error.error_message }}</p>
            <p class="error-endpoint" v-if="error.endpoint">Endpoint: {{ error.endpoint }}</p>
          </div>
        </div>
      </div>

      <!-- Aktualisieren-Button -->
      <div class="actions-section">
        <button @click="refreshData" class="btn-primary" :disabled="loading">
          {{ loading ? 'Lade...' : 'Daten aktualisieren' }}
        </button>
      </div>

      <div class="back-section">
        <button @click="$router.push('/dashboard')" class="btn-secondary">
  ← Zurück zum Dashboard
</button>
      </div>
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const isAllowed = computed(() => authStore.isSuperadmin || authStore.isPartner)

const performance = ref({})
const system = ref({})
const errors = ref({})
const loading = ref(false)
const overallStatus = ref('healthy')

const overallStatusText = computed(() => {
  switch (overallStatus.value) {
    case 'healthy': return 'Gesund'
    case 'degraded': return 'Beeinträchtigt'
    case 'warning': return 'Warnung'
    case 'error': return 'Fehler'
    default: return 'Unbekannt'
  }
})

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString('de-DE')
}

const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchPerformanceData(),
      fetchSystemData(),
      fetchErrorData()
    ])
  } catch (error) {
    console.error('Fehler beim Laden der Monitoring-Daten:', error)
  } finally {
    loading.value = false
  }
}

const fetchPerformanceData = async () => {
  try {
    const response = await fetch('/monitoring/performance')
    if (response.ok) {
      performance.value = await response.json()
    }
  } catch (error) {
    console.error('Fehler beim Laden der Performance-Daten:', error)
  }
}

const fetchSystemData = async () => {
  try {
    const response = await fetch('/monitoring/system')
    if (response.ok) {
      system.value = await response.json()
    }
  } catch (error) {
    console.error('Fehler beim Laden der System-Daten:', error)
  }
}

const fetchErrorData = async () => {
  try {
    const response = await fetch('/monitoring/errors')
    if (response.ok) {
      errors.value = await response.json()
    }
  } catch (error) {
    console.error('Fehler beim Laden der Fehler-Daten:', error)
  }
}

onMounted(() => {
  if (isAllowed.value) {
  refreshData()
  }
})
</script>

<!-- Styles werden aus globaler index.css verwendet --> 