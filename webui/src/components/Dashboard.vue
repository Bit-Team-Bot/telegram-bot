<template>
  <div class="dashboard">
    <!-- Quick Stats -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <h3 class="stat-title">Aktive Gruppen</h3>
          <p class="stat-value">{{ stats.activeGroups }}</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">💰</div>
        <div class="stat-content">
          <h3 class="stat-title">Zahlungen</h3>
          <p class="stat-value">{{ stats.totalPayments }}</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">📅</div>
        <div class="stat-content">
          <h3 class="stat-title">Tage verbleibend</h3>
          <p class="stat-value">{{ stats.daysRemaining }}</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">⚡</div>
        <div class="stat-content">
          <h3 class="stat-title">Features</h3>
          <p class="stat-value">{{ stats.availableFeatures }}</p>
        </div>
      </div>
    </div>

    <!-- Hauptinhalt: ab hier die dashboard-section-Boxen in ein Grid packen -->
    <div class="dashboard-sections-grid">
      <div class="dashboard-section">
        <h2 class="section-title">Paket Status</h2>
        <div class="package-info">
          <div class="package-card" :class="userInfo.package_status">
            <div class="package-header">
              <h3 class="package-name">{{ getPackageName(userInfo.package_status) }}</h3>
              <span class="package-price">{{ getPackagePrice(userInfo.package_status) }}</span>
            </div>
            <p class="package-description">
              {{ getPackageDescription(userInfo.package_status) }}
            </p>
            <div class="package-features">
              <ul class="features-list">
                <li v-if="userInfo.package_status === 'basic'" v-for="feature in getPackageFeatures(userInfo.package_status)" :key="feature">
                  ✅ {{ getFeatureName(feature) }}
                </li>
                <li v-else-if="userInfo.package_status === 'pro'">
                  Enthält alle Funktionen von <b>Basic</b> <br>+ zusätzliche Pro-Features
                </li>
                <li v-else-if="userInfo.package_status === 'expert'">
                  Enthält alle Funktionen von <b>Pro</b> <br>+ zusätzliche Expert-Features
                </li>
                <li v-else-if="userInfo.package_status === 'lifetime'">
                  Enthält alle Funktionen von <b>Expert</b> <br>+ Lifetime-Features
                </li>
              </ul>
            </div>
            <div class="package-actions">
              <button 
                v-if="userInfo.package_status === 'basic'"
                @click="upgradePackage"
                class="action-btn primary"
              >
                Upgrade
              </button>
              <button 
                v-if="userInfo.package_status !== 'basic'"
                @click="manageSubscription"
                class="action-btn secondary"
              >
                Abonnement verwalten
              </button>
            </div>
          </div>
        </div>
      </div>
      <div class="dashboard-section">
        <h2 class="section-title">Letzte Aktivitäten</h2>
        <div class="activity-list">
          <div 
            v-for="activity in recentActivity" 
            :key="activity.id"
            class="activity-item"
          >
            <div class="activity-icon" :class="activity.type">
              {{ getActivityIcon(activity.type) }}
            </div>
            <div class="activity-content">
              <h4 class="activity-title">{{ activity.title }}</h4>
              <p class="activity-description">{{ activity.description }}</p>
              <span class="activity-time">{{ formatTime(activity.timestamp) }}</span>
            </div>
          </div>
        </div>
      </div>
      <div class="dashboard-section">
        <h2 class="section-title">Schnellzugriff</h2>
        <div class="actions-grid">
          <button @click="openGroups" class="action-btn">
            <span class="action-icon">👥</span>
            <span class="action-text">Gruppen verwalten</span>
          </button>
          
          <button @click="openSettings" class="action-btn">
            <span class="action-icon">⚙️</span>
            <span class="action-text">Einstellungen</span>
          </button>
          
          <button @click="openPayments" class="action-btn">
            <span class="action-icon">💳</span>
            <span class="action-text">Zahlungshistorie</span>
          </button>
          
          <button @click="openSupport" class="action-btn">
            <span class="action-icon">🆘</span>
            <span class="action-text">Support</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Payment Status -->
    <div v-if="pendingPayment" class="payment-notification">
      <div class="notification-content">
        <h3 class="notification-title">Ausstehende Zahlung</h3>
        <p class="notification-description">Sie haben eine ausstehende Zahlung. Bitte schließen Sie diese ab, um Ihre Dienste weiterhin nutzen zu können.</p>
        <div class="notification-actions">
          <button @click="completePayment" class="action-btn primary">
            Zahlung abschließen
          </button>
          <button @click="cancelPayment" class="action-btn secondary">
            Abbrechen
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import api from '../api'

export default {
  name: 'Dashboard',
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()
    
    // Reactive data
    const userInfo = ref({})
    const stats = ref({
      activeGroups: 0,
      totalPayments: 0,
      daysRemaining: 0,
      availableFeatures: 0
    })
    const recentActivity = ref([])
    const pendingPayment = ref(null)
    const loading = ref(true)

    // Computed properties
    const isAuthenticated = computed(() => authStore.isAuthenticated)
    const currentUser = computed(() => authStore.user)

    // Methods
    const loadDashboardData = async () => {
      try {
        loading.value = true
        
        // User info laden
        const userResponse = await api.get('/auth/me')
        userInfo.value = userResponse.data
        
        // Stats laden
        const statsResponse = await api.get('/dashboard/stats')
        stats.value = statsResponse.data
        
        // Recent activity laden
        const activityResponse = await api.get('/dashboard/activity')
        recentActivity.value = activityResponse.data
        
        // Pending payment prüfen
        const paymentResponse = await api.get('/payments/pending')
        pendingPayment.value = paymentResponse.data
        
      } catch (error) {
        console.error('Fehler beim Laden der Dashboard-Daten:', error)
      } finally {
        loading.value = false
      }
    }

    const getPackageName = (packageType) => {
      const names = {
        basic: 'Basic',
        pro: 'Pro',
        expert: 'Expert',
        lifetime: 'Lifetime'
      }
      return names[packageType] || 'Unbekannt'
    }

    const getPackagePrice = (packageType) => {
      const prices = {
        basic: 'Kostenlos',
        pro: '€29.99/Monat',
        expert: '€79.99/Monat',
        lifetime: '€299.99'
      }
      return prices[packageType] || 'Unbekannt'
    }

    const getPackageDescription = (packageType) => {
      const descriptions = {
        basic: 'Grundlegende Funktionen für den Einstieg',
        pro: 'Erweiterte Features für aktive Trader',
        expert: 'Professionelle Tools für Experten',
        lifetime: 'Lebenslanger Zugang zu allen Features'
      }
      return descriptions[packageType] || 'Paket-Beschreibung nicht verfügbar'
    }

    const getPackageFeatures = (packageType) => {
      const features = {
        basic: ['basic_groups', 'basic_analytics'],
        pro: ['basic_groups', 'basic_analytics', 'advanced_groups', 'priority_support'],
        expert: ['basic_groups', 'basic_analytics', 'advanced_groups', 'priority_support', 'custom_features', 'api_access'],
        lifetime: ['basic_groups', 'basic_analytics', 'advanced_groups', 'priority_support', 'custom_features', 'api_access', 'lifetime_access']
      }
      return features[packageType] || []
    }

    const getFeatureName = (feature) => {
      const featureNames = {
        basic_groups: 'Grundlegende Gruppen',
        basic_analytics: 'Basis-Analytics',
        advanced_groups: 'Erweiterte Gruppen',
        priority_support: 'Prioritäts-Support',
        custom_features: 'Individuelle Features',
        api_access: 'API-Zugang',
        lifetime_access: 'Lebenslanger Zugang',
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
      }
      return featureNames[feature] || feature
    }

    const getActivityIcon = (type) => {
      const icons = {
        login: '🔐',
        payment: '💳',
        group_created: '👥',
        group_updated: '✏️',
        package_upgraded: '⬆️',
        support_request: '🆘'
      }
      return icons[type] || '📝'
    }

    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleString('de-DE')
    }

    const upgradePackage = () => {
      router.push('/packages')
    }

    const manageSubscription = () => {
      router.push('/subscription')
    }

    const openGroups = () => {
      router.push('/groups')
    }

    const openSettings = () => {
      router.push('/settings')
    }

    const openPayments = () => {
      router.push('/payments')
    }

    const openSupport = () => {
      router.push('/support')
    }

    const completePayment = async () => {
      try {
        if (pendingPayment.value) {
          const response = await api.post(`/payments/${pendingPayment.value.id}/complete`)
          if (response.success) {
            pendingPayment.value = null
            await loadDashboardData()
          }
        }
      } catch (error) {
        console.error('Fehler beim Abschließen der Zahlung:', error)
      }
    }

    const cancelPayment = async () => {
      try {
        if (pendingPayment.value) {
          const response = await api.post(`/payments/${pendingPayment.value.id}/cancel`)
          if (response.success) {
            pendingPayment.value = null
            await loadDashboardData()
          }
        }
      } catch (error) {
        console.error('Fehler beim Abbrechen der Zahlung:', error)
      }
    }

    // Mounting
    onMounted(() => {
      loadDashboardData()
    })

    return {
      userInfo,
      stats,
      recentActivity,
      pendingPayment,
      loading,
      isAuthenticated,
      currentUser,
      getPackageName,
      getPackagePrice,
      getPackageDescription,
      getPackageFeatures,
      getFeatureName,
      getActivityIcon,
      formatTime,
      upgradePackage,
      manageSubscription,
      openGroups,
      openSettings,
      openPayments,
      openSupport,
      completePayment,
      cancelPayment
    }
  }
}
</script>

<style scoped>
/* Hier ggf. deine bisherigen Styles wieder einfügen, falls sie versehentlich entfernt wurden. */
</style>