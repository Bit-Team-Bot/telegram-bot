<template>
  <div class="dashboard-container">
    <!-- Header Section -->
    <div class="header-section">
      <img src="@/assets/wallstreet-header.png" alt="Wallstreet Crypto Header" class="header-image" />
    </div>
    
    <!-- User Role Box für Paketstatus -->
    <div class="user-role-box">
      <div class="role-content">
        <!-- Current Package Info -->
        <div v-if="currentPackage.has_package" class="current-package-info">
          <h3>🎯 Ihr aktuelles Paket</h3>
          <div class="current-package-card">
            <div class="package-info">
              <h4>{{ currentPackage.template?.display_name || currentPackage.package.name }}</h4>
              <p class="package-status">Status: {{ currentPackage.package.status }}</p>
              <p class="package-dates">
                {{ formatDate(currentPackage.package.start_date) }} - {{ formatDate(currentPackage.package.end_date) }}
              </p>
            </div>
            <div class="package-features">
              <h5>Features:</h5>
              <ul>
                <li v-for="(value, key) in currentPackage.features" :key="key">
                  {{ key }}: {{ value ? '✅' : '❌' }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Main Content -->
    <div class="main-content">
      <div class="page-header">
        <h1 class="page-title">Pakete & Add-ons</h1>
        <p class="page-subtitle">Wählen Sie Ihr Trading-Paket und erweitern Sie es mit Add-ons</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Lade Pakete...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-container">
        <p class="error-message">{{ error }}</p>
        <button @click="loadPackages" class="btn-primary">Erneut versuchen</button>
      </div>

      <!-- Available Packages -->
      <div v-if="packages.length > 0" class="packages-section">
        <h3>📦 Verfügbare Pakete</h3>
        <div class="nav-grid">
        <div 
          v-for="pkg in packages" 
          :key="pkg.id" 
          class="nav-card"
          :class="{ featured: pkg.featured, selected: selectedPackage?.id === pkg.id }"
        >
          <div v-if="pkg.featured" class="package-badge">Empfohlen</div>
          <div class="card-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="currentColor"/>
            </svg>
          </div>
          <h3 class="card-title">{{ pkg.display_name }}</h3>
          <p class="card-description">
            <div v-if="pkg.monthly_price">€{{ pkg.monthly_price }}/Monat</div>
            <div v-if="pkg.one_time_price">€{{ pkg.one_time_price }} einmalig</div>
          </p>
          
          <div class="package-features">
            <h5>Features:</h5>
            <ul>
              <template v-if="Object.values(pkg.features).filter(v => v).length === 0">
                <li>Keine Features enthalten</li>
              </template>
              <template v-else>
                <li v-for="key in getAdditionalFeatures(pkg, packages)" :key="key">
                  ✅ {{ getFeatureName(key) }}
                </li>
              </template>
            </ul>
            <button class="btn-secondary mt-2" @click="router.push(`/packages/details/${pkg.id}`)">
              Alle Features anzeigen
            </button>
          </div>

          <div v-if="pkg.available_addons && pkg.available_addons.length > 0" class="package-addons">
            <h5>Verfügbare Add-ons:</h5>
            <ul>
              <li v-for="addon in pkg.available_addons" :key="addon.id">
                {{ addon.display_name }}
              </li>
            </ul>
          </div>

          <button 
            @click="selectPackage(pkg)" 
            class="btn-primary package-button"
            :disabled="loading"
          >
            {{ selectedPackage?.id === pkg.id ? 'Ausgewählt' : 'Paket auswählen' }}
          </button>
        </div>
        </div>
      </div>

      <!-- Available Add-ons -->
      <div v-if="currentPackage.has_package && availableAddons.length > 0" class="addons-section">
        <h3>🔧 Verfügbare Add-ons</h3>
        <div class="nav-grid">
          <div 
            v-for="addon in availableAddons" 
            :key="addon.id" 
            class="nav-card"
          >
            <div class="card-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="currentColor"/>
              </svg>
            </div>
            <h3 class="card-title">{{ addon.display_name }}</h3>
            <p class="card-description">
              <div v-if="addon.monthly_price">€{{ addon.monthly_price }}/Monat</div>
              <div v-if="addon.one_time_price">€{{ addon.one_time_price }} einmalig</div>
            </p>
            
            <p class="addon-description">{{ addon.description }}</p>
            
            <div v-if="addon.tiers && addon.tiers.length > 0" class="addon-tiers">
              <h5>Tiers:</h5>
              <div class="tiers-list">
                <div v-for="tier in addon.tiers" :key="tier.id" class="tier-item">
                  <span class="tier-level">{{ tier.level }}</span>
                  <span class="tier-price">€{{ tier.price }}</span>
                  <span class="tier-description">{{ tier.description }}</span>
                </div>
              </div>
            </div>

            <button 
              @click="bookAddon(addon)" 
              class="btn-secondary addon-button"
              :disabled="loading"
            >
              Add-on buchen
            </button>
          </div>
        </div>
      </div>

      <!-- Selected Package Summary -->
      <div v-if="selectedPackage" class="user-role-box">
        <div class="role-content">
          <h3>Ausgewähltes Paket: {{ selectedPackage.display_name }}</h3>
          <div class="selected-package-details">
            <p v-if="selectedPackage.monthly_price">Monatspreis: €{{ selectedPackage.monthly_price }}</p>
            <p v-if="selectedPackage.one_time_price">Einmalpreis: €{{ selectedPackage.one_time_price }}</p>
          </div>
          <button @click="purchasePackage" class="btn-primary" :disabled="loading">
            {{ loading ? 'Verarbeite...' : 'Jetzt kaufen' }}
          </button>
        </div>
      </div>

      <div class="back-section">
        <button @click="$router.push('/dashboard')" class="btn-secondary">
          ← Zurück zum Dashboard
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router = useRouter()
const authStore = useAuthStore()
const packages = ref([])
const selectedPackage = ref(null)
const currentPackage = ref({ has_package: false })
const availableAddons = ref([])
const loading = ref(false)
const error = ref(null)

const loadPackages = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Lade verfügbare Pakete
    const packagesResponse = await api.get('/user/packages/available')
    packages.value = packagesResponse.data
    console.log('✅ Pakete geladen:', packages.value)
    
    // Lade aktuelles Paket
    const currentResponse = await api.get('/user/packages/current')
    currentPackage.value = currentResponse.data
    console.log('✅ Aktuelles Paket geladen:', currentPackage.value)
    
    // Lade verfügbare Add-ons (nur wenn User ein Paket hat)
    if (currentPackage.value.has_package) {
      const addonsResponse = await api.get('/user/packages/addons')
      availableAddons.value = addonsResponse.data
      console.log('✅ Add-ons geladen:', availableAddons.value)
    }
  } catch (err) {
    console.error('❌ Fehler beim Laden der Pakete:', err)
    error.value = 'Fehler beim Laden der Pakete. Bitte versuchen Sie es erneut.'
  } finally {
    loading.value = false
  }
}

const selectPackage = (pkg) => {
  selectedPackage.value = pkg
  console.log('📦 Paket ausgewählt:', pkg)
}

const purchasePackage = async () => {
  if (!selectedPackage.value) return
  
  loading.value = true
  
  try {
    const response = await api.post('/payments/create', {
      package_template_id: selectedPackage.value.id,
      amount: selectedPackage.value.monthly_price || selectedPackage.value.one_time_price
    })
    
    console.log('✅ Zahlung erstellt:', response.data)
    
    // Leite zur Zahlungsseite weiter
    router.push('/payments')
  } catch (err) {
    console.error('❌ Fehler beim Erstellen der Zahlung:', err)
    error.value = 'Fehler beim Erstellen der Zahlung. Bitte versuchen Sie es erneut.'
  } finally {
    loading.value = false
  }
}

const bookAddon = async (addon) => {
  loading.value = true
  
  try {
    const response = await api.post(`/user/packages/addons/${addon.id}/book`)
    
    console.log('✅ Add-on gebucht:', response.data)
    
    // Aktualisiere die Daten
    await loadPackages()
    
    // Zeige Erfolgsmeldung
    alert(`Add-on "${addon.display_name}" wurde erfolgreich gebucht!`)
  } catch (err) {
    console.error('❌ Fehler beim Buchen des Add-ons:', err)
    error.value = err.response?.data?.detail || 'Fehler beim Buchen des Add-ons. Bitte versuchen Sie es erneut.'
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Unbekannt'
  return new Date(dateString).toLocaleDateString('de-DE')
}

// Hilfsfunktion für Klartextnamen
const getFeatureName = (key) => {
  const featureNames = {
    message_forwarding_basic: 'Nachrichten-Weiterleitung (Basic)',
    message_forwarding_pro: 'Nachrichten-Weiterleitung (Pro)',
    message_forwarding_expert: 'Nachrichten-Weiterleitung (Expert)',
    group_management_basic: 'Gruppenverwaltung (Basic)',
    group_management_pro: 'Gruppenverwaltung (Pro)',
    group_management_expert: 'Gruppenverwaltung (Expert)',
    signal_groups_basic: 'Signalgruppen (Basic)',
    signal_groups_pro: 'Signalgruppen (Pro)',
    signal_groups_expert: 'Signalgruppen (Expert)',
    usdt_billing: 'USDT-Abrechnung',
    user_management: 'Benutzerverwaltung',
    mobile_first_optimization: 'Mobile-First-Optimierung',
    bot_admin_panel: 'Bot-Admin-Panel',
    api_webhooks: 'API Webhooks',
    media_forwarding: 'Medien-Weiterleitung',
    advanced_filter_logic: 'Erweiterte Filterlogik',
    activity_logs: 'Aktivitätsprotokolle',
    email_notifications: 'E-Mail-Benachrichtigungen',
    time_scheduled_forwarding: 'Zeitgesteuerte Weiterleitung',
    text_replacement_rules: 'Text-Ersetzungsregeln',
    duplicate_filter: 'Duplikat-Filter',
    webhook_triggered_messages: 'Webhook-gesteuerte Nachrichten',
    message_statistics: 'Nachrichten-Statistiken',
    anonymous_forwarding: 'Anonyme Weiterleitung',
    auto_group_welcome: 'Automatische Gruppen-Begrüßung',
    invite_link_generator: 'Einladungslink-Generator',
    group_backup_restore: 'Gruppen-Backup & Wiederherstellung',
    user_limit_per_group: 'User-Limit pro Gruppe',
    auto_kick_bots_spam: 'Auto-Kick für Bots/Spam',
    performance_tracking: 'Performance-Tracking',
    signal_notifications: 'Signal-Benachrichtigungen',
    individual_notification_settings: 'Individuelle Benachrichtigungseinstellungen',
    external_signal_api: 'Externe Signal-API',
    multi_language_support: 'Mehrsprachigkeit',
    darkmode_webui: 'Darkmode WebUI',
    lifetime_monthly_model: 'Lifetime/Monats-Modell',
    auto_invoice_email: 'Automatische Rechnungs-E-Mail',
    custom_package_upgrades: 'Individuelle Paket-Upgrades',
    free_trial_7_days: '7 Tage kostenlos testen',
    custom_branding: 'Eigenes Branding',
    '2fa_telegram_code': '2FA Telegram-Code',
    ip_whitelist_blacklist: 'IP-Whitelist/Blacklist',
    api_access_logging: 'API-Access-Logging',
    webhook_all_actions: 'Webhooks für alle Aktionen',
    backup_settings: 'Backup-Einstellungen',
    export_import_config: 'Export/Import Konfiguration',
  };
  return featureNames[key] || key;
};

// Hilfsfunktion: Features pro Paket als Array (nur aktivierte)
const getActiveFeatures = (pkg) => {
  return Object.entries(pkg.features)
    .filter(([_, value]) => value)
    .map(([key]) => key)
}

// Hilfsfunktion: Zusätzliche Features gegenüber dem Vorgängerpaket
const getAdditionalFeatures = (pkg, allPackages) => {
  const idx = allPackages.findIndex(p => p.id === pkg.id)
  if (idx === 0) return getActiveFeatures(pkg)
  const prevFeatures = new Set(getActiveFeatures(allPackages[idx - 1]))
  return getActiveFeatures(pkg).filter(f => !prevFeatures.has(f))
}

onMounted(() => {
  loadPackages()
})
</script>

<!-- Styles werden aus globaler index.css verwendet --> 