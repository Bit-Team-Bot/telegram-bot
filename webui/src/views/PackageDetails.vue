<template>
  <div class="package-details-container">
    <main class="package-details-content">
      <div class="page-header">
        <h1 class="page-title">Paket-Details</h1>
        <p class="page-subtitle">Alle enthaltenen Features im Überblick</p>
      </div>
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Lade Paketdaten...</p>
      </div>
      <div v-else-if="error" class="error-container">
        <p class="error-message">{{ error }}</p>
        <button @click="loadPackage" class="btn-primary">Erneut versuchen</button>
      </div>
      <div v-else-if="pkg" class="package-details-card">
        <h2 class="package-name">{{ pkg.display_name }}</h2>
        <div class="package-pricing">
          <span v-if="pkg.monthly_price">Monatspreis: €{{ pkg.monthly_price }}</span>
          <span v-if="pkg.one_time_price">Einmalpreis: €{{ pkg.one_time_price }}</span>
        </div>
        <div class="package-features">
          <h3>Enthaltene Features:</h3>
          <ul>
            <li v-for="key in allFeatures" :key="key">
              ✅ {{ getFeatureName(key) }}
            </li>
          </ul>
        </div>
        <button class="btn-secondary mt-4" @click="goBack">Zurück zur Übersicht</button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

const route = useRoute()
const router = useRouter()
const pkg = ref(null)
const allPackages = ref([])
const loading = ref(false)
const error = ref(null)
const allFeatures = ref([])

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

const getActiveFeatures = (pkg) => {
  return Object.entries(pkg.features)
    .filter(([_, value]) => value)
    .map(([key]) => key)
}

const getAllFeatures = (pkg, allPkgs) => {
  // Alle Features dieses Pakets und aller Vorgängerpakete
  const idx = allPkgs.findIndex(p => p.id === pkg.id)
  let features = new Set()
  for (let i = 0; i <= idx; i++) {
    getActiveFeatures(allPkgs[i]).forEach(f => features.add(f))
  }
  return Array.from(features)
}

const loadPackage = async () => {
  loading.value = true
  error.value = null
  try {
    // Alle Pakete laden (für Feature-Vergleich)
    const packagesResponse = await api.get('/user/packages/available')
    allPackages.value = packagesResponse.data
    // Das aktuelle Paket finden
    const found = allPackages.value.find(p => p.id == route.params.id)
    if (!found) throw new Error('Paket nicht gefunden')
    pkg.value = found
    allFeatures.value = getAllFeatures(pkg.value, allPackages.value)
  } catch (err) {
    error.value = err.message || 'Fehler beim Laden des Pakets.'
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/packages')
}

onMounted(() => {
  loadPackage()
})
</script>

<style scoped>
.package-details-container {
  min-height: 100vh;
  background-color: var(--bg-primary);
  display: flex;
  flex-direction: column;
}
.package-details-content {
  flex: 1;
  padding: 24px;
  max-width: 600px;
  margin: 0 auto;
  width: 100%;
}
.page-header {
  text-align: center;
  margin-bottom: 32px;
}
.page-title {
  font-size: 2rem;
  font-weight: bold;
  color: var(--text-white);
  margin: 0 0 8px 0;
}
.page-subtitle {
  color: var(--text-gray);
  font-size: 1.1rem;
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
.package-details-card {
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius);
  padding: 32px;
  box-shadow: var(--shadow-3d);
  margin-bottom: 32px;
  text-align: center;
}
.package-name {
  color: var(--accent-orange);
  font-size: 1.4rem;
  margin-bottom: 8px;
}
.package-pricing {
  color: var(--text-gray);
  margin-bottom: 16px;
}
.package-features h3 {
  color: var(--text-white);
  margin-bottom: 12px;
}
.package-features ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.package-features li {
  color: var(--text-white);
  margin-bottom: 6px;
  font-size: 1rem;
}
.btn-secondary {
  background: var(--bg-secondary);
  color: var(--accent-orange);
  border: 1px solid var(--accent-orange);
  border-radius: 8px;
  padding: 10px 20px;
  font-weight: bold;
  cursor: pointer;
  margin-top: 16px;
  transition: background 0.2s;
}
.btn-secondary:hover {
  background: var(--accent-orange);
  color: var(--bg-primary);
}
</style> 