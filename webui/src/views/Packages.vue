<template>
  <div class="packages-container">
    <main class="packages-content">
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

      <!-- Available Packages -->
      <div v-if="packages.length > 0" class="packages-section">
        <h3>📦 Verfügbare Pakete</h3>
        <div class="packages-grid">
        <div 
          v-for="pkg in packages" 
          :key="pkg.id" 
          class="package-card"
          :class="{ featured: pkg.featured, selected: selectedPackage?.id === pkg.id }"
        >
          <div v-if="pkg.featured" class="package-badge">Empfohlen</div>
          <div class="package-header">
              <h3 class="package-name">{{ pkg.display_name }}</h3>
              <div class="package-pricing">
                <div v-if="pkg.monthly_price" class="package-price">€{{ pkg.monthly_price }}/Monat</div>
                <div v-if="pkg.one_time_price" class="package-price">€{{ pkg.one_time_price }} einmalig</div>
              </div>
          </div>
            
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
        <div class="addons-grid">
          <div 
            v-for="addon in availableAddons" 
            :key="addon.id" 
            class="addon-card"
          >
            <div class="addon-header">
              <h4>{{ addon.display_name }}</h4>
              <div class="addon-pricing">
                <div v-if="addon.monthly_price" class="addon-price">€{{ addon.monthly_price }}/Monat</div>
                <div v-if="addon.one_time_price" class="addon-price">€{{ addon.one_time_price }} einmalig</div>
              </div>
            </div>
            
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
      <div v-if="selectedPackage" class="selected-package">
        <h3>Ausgewähltes Paket: {{ selectedPackage.display_name }}</h3>
        <div class="selected-package-details">
          <p v-if="selectedPackage.monthly_price">Monatspreis: €{{ selectedPackage.monthly_price }}</p>
          <p v-if="selectedPackage.one_time_price">Einmalpreis: €{{ selectedPackage.one_time_price }}</p>
        </div>
        <button @click="purchasePackage" class="btn-primary" :disabled="loading">
          {{ loading ? 'Verarbeite...' : 'Jetzt kaufen' }}
        </button>
      </div>

      <div class="back-section">
        <button @click="$router.push('/dashboard')" class="btn-secondary">
          ← Zurück zum Dashboard
        </button>
      </div>
    </main>
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

<style scoped>
.packages-container {
  min-height: 100vh;
  background-color: var(--bg-primary);
  display: flex;
  flex-direction: column;
}

.packages-content {
  flex: 1;
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.page-header {
  text-align: center;
  margin-bottom: 48px;
}

.page-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: var(--text-white);
  margin: 0 0 16px 0;
}

.page-subtitle {
  color: var(--text-gray);
  font-size: 1.2rem;
  margin: 0;
}

.loading-container {
  text-align: center;
  padding: 48px;
}

.loading-spinner {
  border: 4px solid var(--bg-secondary);
  border-top: 4px solid var(--accent-orange);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container {
  text-align: center;
  padding: 48px;
}

.error-message {
  color: #ff6b6b;
  margin-bottom: 16px;
}

.packages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 48px;
}

.package-card {
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius);
  padding: 32px;
  box-shadow: var(--shadow-3d);
  transition: transform 0.2s ease;
  position: relative;
  border: 2px solid transparent;
}

.package-card:hover {
  transform: translateY(-4px);
}

.package-card.featured {
  border-color: var(--accent-orange);
  transform: scale(1.05);
}

.package-card.featured:hover {
  transform: scale(1.05) translateY(-4px);
}

.package-card.selected {
  border-color: #4CAF50;
  background-color: rgba(76, 175, 80, 0.1);
}

.package-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background-color: var(--accent-orange);
  color: var(--text-white);
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.package-header {
  text-align: center;
  margin-bottom: 24px;
}

.package-name {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--text-white);
  margin: 0 0 8px 0;
}

.package-price {
  font-size: 2.5rem;
  font-weight: bold;
  color: var(--accent-orange);
  margin: 0;
}

.package-features {
  margin-bottom: 32px;
}

.package-features ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.package-features li {
  color: var(--text-white);
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.package-button {
  width: 100%;
  padding: 12px;
  font-size: 1rem;
}

.selected-package {
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius);
  padding: 24px;
  margin-bottom: 32px;
  text-align: center;
  border: 2px solid #4CAF50;
}

.selected-package h3 {
  color: var(--text-white);
  margin: 0 0 8px 0;
}

.selected-package p {
  color: var(--text-gray);
  margin: 0 0 16px 0;
}

.back-section {
  text-align: center;
}

@media (max-width: 768px) {
  .packages-content {
    padding: 16px;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .packages-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .package-card {
    padding: 24px;
  }
}

/* Current Package Info */
.current-package-info {
  margin-bottom: 48px;
}

.current-package-info h3 {
  color: var(--text-white);
  margin-bottom: 16px;
  font-size: 1.5rem;
}

.current-package-card {
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius);
  padding: 24px;
  border: 2px solid var(--accent-orange);
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.package-info h4 {
  color: var(--text-white);
  margin: 0 0 12px 0;
  font-size: 1.3rem;
}

.package-status {
  color: var(--accent-orange);
  font-weight: bold;
  margin: 0 0 8px 0;
}

.package-dates {
  color: var(--text-gray);
  margin: 0;
  font-size: 0.9rem;
}

.package-features h5 {
  color: var(--text-white);
  margin: 0 0 12px 0;
}

.package-features ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.package-features li {
  color: var(--text-white);
  margin-bottom: 4px;
  font-size: 0.9rem;
}

/* Packages Section */
.packages-section {
  margin-bottom: 48px;
}

.packages-section h3 {
  color: var(--text-white);
  margin-bottom: 24px;
  font-size: 1.5rem;
}

.package-pricing {
  text-align: center;
}

.package-price {
  font-size: 1.8rem;
  font-weight: bold;
  color: var(--accent-orange);
  margin: 4px 0;
}

.package-addons {
  margin-top: 16px;
}

.package-addons h5 {
  color: var(--text-white);
  margin: 0 0 8px 0;
  font-size: 0.9rem;
}

.package-addons ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.package-addons li {
  color: var(--text-gray);
  font-size: 0.8rem;
  margin-bottom: 2px;
}

/* Add-ons Section */
.addons-section {
  margin-bottom: 48px;
}

.addons-section h3 {
  color: var(--text-white);
  margin-bottom: 24px;
  font-size: 1.5rem;
}

.addons-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.addon-card {
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius);
  padding: 20px;
  box-shadow: var(--shadow-3d);
  transition: transform 0.2s ease;
  border: 2px solid transparent;
}

.addon-card:hover {
  transform: translateY(-2px);
}

.addon-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.addon-header h4 {
  color: var(--text-white);
  margin: 0;
  font-size: 1.1rem;
}

.addon-pricing {
  text-align: right;
}

.addon-price {
  color: var(--accent-orange);
  font-weight: bold;
  font-size: 0.9rem;
  margin: 2px 0;
}

.addon-description {
  color: var(--text-gray);
  margin: 0 0 16px 0;
  font-size: 0.9rem;
  line-height: 1.4;
}

.addon-tiers h5 {
  color: var(--text-white);
  margin: 0 0 8px 0;
  font-size: 0.9rem;
}

.tiers-list {
  margin-bottom: 16px;
}

.tier-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.tier-item:last-child {
  border-bottom: none;
}

.tier-level {
  color: var(--accent-orange);
  font-weight: bold;
  font-size: 0.8rem;
}

.tier-price {
  color: var(--text-white);
  font-weight: bold;
  font-size: 0.8rem;
}

.tier-description {
  color: var(--text-gray);
  font-size: 0.7rem;
  flex: 1;
  text-align: right;
  margin-left: 8px;
}

.addon-button {
  width: 100%;
  padding: 10px;
  font-size: 0.9rem;
}

/* Selected Package */
.selected-package-details {
  margin-bottom: 16px;
}

.selected-package-details p {
  color: var(--text-gray);
  margin: 4px 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .current-package-card {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .addons-grid {
    grid-template-columns: 1fr;
  }
  
  .addon-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .addon-pricing {
    text-align: left;
    margin-top: 8px;
  }
  
  .tier-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .tier-description {
    text-align: left;
    margin-left: 0;
  }
}
</style> 