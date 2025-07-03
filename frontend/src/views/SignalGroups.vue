<template>
  <div class="signal-groups-page">
    <div class="header">
      <h1>Signal-Gruppen System</h1>
      <p>Automatische Weiterleitung von Signalen in thematische Gruppen</p>
    </div>

    <!-- System-Info -->
    <div class="system-info">
      <div class="info-card">
        <h3>Wie funktioniert das System?</h3>
        <div class="info-content">
          <div class="info-step">
            <span class="step-number">1</span>
            <div class="step-content">
              <h4>Userbot-Session verknuepfen</h4>
              <p>Admins/Partner verknuepfen Userbot-Sessions mit Signal-Gruppen</p>
            </div>
          </div>
          <div class="info-step">
            <span class="step-number">2</span>
            <div class="step-content">
              <h4>Thematische Aufteilung</h4>
              <p>Nachrichten werden automatisch nach Themen sortiert (BTC, Altcoins, DeFi)</p>
            </div>
          </div>
          <div class="info-step">
            <span class="step-number">3</span>
            <div class="step-content">
              <h4>Flexible Abonnements</h4>
              <p>User koennen einzelne Themen oder komplette Pakete abonnieren</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Verfügbare Signal-Gruppen -->
    <div class="signal-groups-section">
      <h2>Verfügbare Signal-Gruppen</h2>
      <div class="signal-groups-grid">
        <div 
          v-for="group in signalGroups" 
          :key="group.id" 
          class="signal-group-card"
          :class="{ 'partner-group': group.partner_id }"
        >
          <div class="group-header">
            <h3>{{ group.name }}</h3>
            <div class="group-badges">
              <span v-if="group.partner_id" class="badge partner">Partner</span>
              <span v-if="group.auto_create_groups" class="badge auto">Auto-Erstellung</span>
              <span v-if="group.userbot_session_id" class="badge linked">Userbot verknuepft</span>
            </div>
          </div>
          
          <p class="group-description">{{ group.description }}</p>
          
          <div class="group-theme" v-if="group.theme">
            <strong>Thema:</strong> {{ group.theme }}
          </div>
          
          <div class="group-config" v-if="group.auto_forward_messages">
            <div class="config-item">
              <span class="config-label">Auto-Weiterleitung:</span>
              <span class="config-value">Aktiv</span>
            </div>
            <div class="config-item" v-if="group.forward_delay_seconds > 0">
              <span class="config-label">Verzögerung:</span>
              <span class="config-value">{{ group.forward_delay_seconds }}s</span>
            </div>
            <div class="config-item" v-if="group.max_members_per_group">
              <span class="config-label">Max. Mitglieder:</span>
              <span class="config-value">{{ group.max_members_per_group }}</span>
            </div>
          </div>
          
          <!-- Thematische Gruppen -->
          <div class="themes-section" v-if="group.themes && group.themes.length > 0">
            <h4>Thematische Gruppen</h4>
            <div class="themes-grid">
              <div 
                v-for="theme in group.themes" 
                :key="theme.id" 
                class="theme-card"
                :class="{ 'subscribed': theme.is_subscribed }"
              >
                <div class="theme-header">
                  <h5>{{ theme.name }}</h5>
                  <span class="theme-price">€{{ theme.price_monthly }}/Monat</span>
                </div>
                <p class="theme-description">{{ theme.description }}</p>
                <div class="theme-status">
                  <span v-if="theme.is_subscribed" class="status subscribed">
                    Abonniert
                  </span>
                  <button 
                    v-else 
                    @click="subscribeToTheme(group.id, theme.id, theme.price_monthly)"
                    class="btn-subscribe"
                  >
                    Abonnieren
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div class="price-staffel">
            <h4>Komplettpaket-Preise:</h4>
            <div class="price-list">
              <div class="price-item" v-for="i in 5" :key="i">
                <span class="group-count">{{ i }} {{ i === 1 ? 'Gruppe' : 'Gruppen' }}</span>
                <span class="price">€{{ getGroupPrice(group, i) }}</span>
              </div>
            </div>
          </div>
          
          <div class="group-actions">
            <button 
              @click="viewGroupDetails(group)" 
              class="btn-primary"
            >
              Details & Themen
            </button>
            <button 
              v-if="!group.userbot_session_id"
              @click="linkUserbotSession(group)" 
              class="btn-secondary"
            >
              Userbot verknuepfen
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Meine Abonnements -->
    <div class="subscriptions-section" v-if="userSubscriptions.length > 0">
      <h2>Meine Abonnements</h2>
      <div class="subscriptions-grid">
        <div 
          v-for="subscription in userSubscriptions" 
          :key="subscription.id" 
          class="subscription-card"
        >
          <div class="subscription-header">
            <h3>{{ getGroupName(subscription.signal_group_id) }}</h3>
            <span class="subscription-status" :class="subscription.status">
              {{ subscription.status === 'active' ? 'Aktiv' : 'Inaktiv' }}
            </span>
          </div>
          
          <div class="subscription-details">
            <div class="detail-row">
              <span class="label">Gruppen:</span>
              <span class="value">{{ subscription.group_count }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Start:</span>
              <span class="value">{{ formatDate(subscription.start_date) }}</span>
            </div>
            <div class="detail-row" v-if="subscription.end_date">
              <span class="label">Ende:</span>
              <span class="value">{{ formatDate(subscription.end_date) }}</span>
            </div>
          </div>
          
          <div class="subscription-actions">
            <button @click="manageSubscription(subscription)" class="btn-secondary">
              Verwalten
            </button>
            <button @click="cancelSubscription(subscription)" class="btn-danger">
              Kuendigen
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Thematische Abonnements -->
    <div class="theme-subscriptions-section" v-if="themeSubscriptions.length > 0">
      <h2>Meine Themen-Abonnements</h2>
      <div class="theme-subscriptions-grid">
        <div 
          v-for="subscription in themeSubscriptions" 
          :key="subscription.id" 
          class="theme-subscription-card"
        >
          <div class="subscription-header">
            <h3>{{ getThemeName(subscription.theme_id) }}</h3>
            <span class="subscription-status" :class="subscription.status">
              {{ subscription.status === 'active' ? 'Aktiv' : 'Inaktiv' }}
            </span>
          </div>
          
          <div class="subscription-details">
            <div class="detail-row">
              <span class="label">Preis:</span>
              <span class="value">€{{ subscription.monthly_price }}/Monat</span>
            </div>
            <div class="detail-row">
              <span class="label">Start:</span>
              <span class="value">{{ formatDate(subscription.start_date) }}</span>
            </div>
            <div class="detail-row" v-if="subscription.end_date">
              <span class="label">Ende:</span>
              <span class="value">{{ formatDate(subscription.end_date) }}</span>
            </div>
          </div>
          
          <div class="subscription-actions">
            <button @click="cancelThemeSubscription(subscription)" class="btn-danger">
              Kuendigen
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Userbot-Session verknuepfen Modal -->
    <div v-if="showLinkModal" class="modal-overlay" @click="closeLinkModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Userbot-Session verknuepfen: {{ selectedGroup?.name }}</h3>
          <button @click="closeLinkModal" class="btn-close">&times;</button>
        </div>
        
        <form @submit.prevent="linkUserbotToGroup" class="modal-form">
          <div class="form-group">
            <label>Userbot-Session auswählen</label>
            <select v-model="linkData.userbot_session_id" class="form-control" required>
              <option value="">Session auswählen...</option>
              <option v-for="session in availableUserbotSessions" :key="session.id" :value="session.id">
                {{ session.session_name }} ({{ session.session_type }})
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Zielgruppen (Telegram-Gruppen-IDs)</label>
            <textarea 
              v-model="linkData.target_groups" 
              class="form-control"
              rows="3"
              placeholder="-1001234567890, -1001234567891"
            ></textarea>
            <small class="form-help">Komma-getrennte Liste der Telegram-Gruppen-IDs</small>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeLinkModal" class="btn-secondary">
              Abbrechen
            </button>
            <button type="submit" class="btn-primary">
              Verknuepfen
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Thema abonnieren Modal -->
    <div v-if="showThemeModal" class="modal-overlay" @click="closeThemeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Thema abonnieren: {{ selectedTheme?.name }}</h3>
          <button @click="closeThemeModal" class="btn-close">&times;</button>
        </div>
        
        <div class="modal-form">
          <div class="theme-info">
            <h4>Thema: {{ selectedTheme?.name }}</h4>
            <p>{{ selectedTheme?.description }}</p>
            <div class="price-info">
              <strong>Preis:</strong> €{{ selectedTheme?.price_monthly }}/Monat
            </div>
          </div>
          
          <div class="subscription-info">
            <h4>Was Sie erhalten:</h4>
            <ul>
              <li>Automatische Weiterleitung von {{ selectedTheme?.name }}-Signalen</li>
              <li>Thematische Gruppierung</li>
              <li>Monatliche Abrechnung</li>
              <li>Jederzeit kündbar</li>
            </ul>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeThemeModal" class="btn-secondary">
              Abbrechen
            </button>
            <button @click="confirmThemeSubscription" class="btn-primary">
              Abonnement erstellen
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const signalGroups = ref([])
const userSubscriptions = ref([])
const themeSubscriptions = ref([])
const showSubscriptionModal = ref(false)
const showLinkModal = ref(false)
const showThemeModal = ref(false)
const selectedGroup = ref(null)
const selectedTheme = ref(null)
const subscriptionData = ref({
  group_count: 1
})
const linkData = ref({
  userbot_session_id: '',
  target_groups: ''
})

const loadSignalGroups = async () => {
  try {
    const response = await fetch('/api/user/signal-groups', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    if (response.ok) {
      signalGroups.value = await response.json()
    } else {
      console.error('Fehler beim Laden der Signal-Gruppen')
    }
  } catch (error) {
    console.error('Fehler beim Laden der Signal-Gruppen:', error)
  }
}

const loadUserSubscriptions = async () => {
  try {
    const response = await fetch('/api/user/signal-group-subscriptions', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    if (response.ok) {
      userSubscriptions.value = await response.json()
    } else {
      console.error('Fehler beim Laden der Abonnements')
    }
  } catch (error) {
    console.error('Fehler beim Laden der Abonnements:', error)
  }
}

const loadThemeSubscriptions = async () => {
  try {
    const response = await fetch('/api/user/theme-subscriptions', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    if (response.ok) {
      themeSubscriptions.value = await response.json()
    } else {
      console.error('Fehler beim Laden der Themen-Abonnements')
    }
  } catch (error) {
    console.error('Fehler beim Laden der Themen-Abonnements:', error)
  }
}

const getGroupPrice = (group, count) => {
  if (!group) return 0
  switch (count) {
    case 1: return group.price_1_group
    case 2: return group.price_2_groups
    case 3: return group.price_3_groups
    case 4: return group.price_4_groups
    case 5: return group.price_5_groups
    default: return 0
  }
}

const hasActiveSubscription = (groupId) => {
  return userSubscriptions.value.some(sub => 
    sub.signal_group_id === groupId && sub.status === 'active'
  )
}

const getGroupName = (groupId) => {
  const group = signalGroups.value.find(g => g.id === groupId)
  return group ? group.name : 'Unbekannte Gruppe'
}

const getThemeName = (themeId) => {
  const theme = signalGroups.value.find(g => g.themes && g.themes.some(t => t.id === themeId))
  const themeObj = theme?.themes.find(t => t.id === themeId)
  return themeObj ? themeObj.name : 'Unbekanntes Thema'
}

const subscribeToGroup = (group) => {
  selectedGroup.value = group
  subscriptionData.value.group_count = 1
  showSubscriptionModal.value = true
}

const subscribeToTheme = (groupId, themeId, price) => {
  selectedTheme.value = { id: themeId, price_monthly: price }
  showThemeModal.value = true
}

const createSubscription = async () => {
  try {
    const response = await fetch('/api/user/signal-group-subscriptions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        signal_group_id: selectedGroup.value.id,
        group_count: subscriptionData.value.group_count
      })
    })
    
    if (response.ok) {
      await loadUserSubscriptions()
      closeSubscriptionModal()
      alert('Abonnement erfolgreich erstellt!')
    } else {
      const error = await response.json()
      alert(`Fehler: ${error.detail}`)
    }
  } catch (error) {
    console.error('Fehler beim Erstellen des Abonnements:', error)
    alert('Fehler beim Erstellen des Abonnements')
  }
}

const confirmThemeSubscription = async () => {
  try {
    const response = await fetch('/api/user/theme-subscriptions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        theme_id: selectedTheme.value.id,
        monthly_price: selectedTheme.value.price_monthly
      })
    })
    
    if (response.ok) {
      await loadThemeSubscriptions()
      closeThemeModal()
      alert('Thema abonniert!')
    } else {
      const error = await response.json()
      alert(`Fehler: ${error.detail}`)
    }
  } catch (error) {
    console.error('Fehler beim Abonnieren des Themas:', error)
    alert('Fehler beim Abonnieren des Themas')
  }
}

const closeSubscriptionModal = () => {
  showSubscriptionModal.value = false
  selectedGroup.value = null
  subscriptionData.value.group_count = 1
}

const closeThemeModal = () => {
  showThemeModal.value = false
  selectedTheme.value = null
}

const viewGroupDetails = (group) => {
  // Implementierung für Gruppen-Details
  console.log('Gruppen-Details:', group)
}

const manageSubscription = (subscription) => {
  // Implementierung für Abonnement-Verwaltung
  console.log('Abonnement verwalten:', subscription)
}

const cancelSubscription = (subscription) => {
  if (confirm('Moechten Sie dieses Abonnement wirklich kuendigen?')) {
    // Implementierung für Abonnement-Kündigung
    console.log('Abonnement kuendigen:', subscription)
  }
}

const cancelThemeSubscription = (subscription) => {
  if (confirm('Moechten Sie dieses Themaabonnement wirklich kuendigen?')) {
    // Implementierung für Themaabonnement-Kündigung
    console.log('Themaabonnement kuendigen:', subscription)
  }
}

const linkUserbotToGroup = async () => {
  try {
    const response = await fetch('/api/user/link-userbot-session', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        userbot_session_id: linkData.value.userbot_session_id,
        target_groups: linkData.value.target_groups.split(',').map(id => id.trim())
      })
    })
    
    if (response.ok) {
      await loadSignalGroups()
      closeLinkModal()
      alert('Userbot-Session verknuepfen!')
    } else {
      const error = await response.json()
      alert(`Fehler: ${error.detail}`)
    }
  } catch (error) {
    console.error('Fehler beim Verknuepfen der Userbot-Session:', error)
    alert('Fehler beim Verknuepfen der Userbot-Session')
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('de-DE', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

onMounted(() => {
  loadSignalGroups()
  loadUserSubscriptions()
  loadThemeSubscriptions()
})
</script>

<style scoped>
.signal-groups-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.header h1 {
  color: #333;
  margin-bottom: 10px;
  font-size: 2.5rem;
}

.header p {
  color: #666;
  font-size: 1.1rem;
}

.system-info {
  margin-bottom: 40px;
}

.info-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.info-card h3 {
  margin-bottom: 20px;
  color: #333;
}

.info-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.info-step {
  display: flex;
  align-items: flex-start;
  gap: 15px;
}

.step-number {
  background: #007bff;
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.step-content h4 {
  margin: 0 0 8px 0;
  color: #333;
}

.step-content p {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
}

.signal-groups-section,
.subscriptions-section,
.theme-subscriptions-section {
  margin-bottom: 40px;
}

.signal-groups-section h2,
.subscriptions-section h2,
.theme-subscriptions-section h2 {
  margin-bottom: 20px;
  color: #333;
}

.signal-groups-grid,
.subscriptions-grid,
.theme-subscriptions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.signal-group-card,
.subscription-card,
.theme-subscription-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
}

.signal-group-card.partner-group {
  border-left: 4px solid #28a745;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.group-header h3 {
  margin: 0;
  color: #333;
}

.group-badges {
  display: flex;
  gap: 8px;
}

.badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.badge.partner {
  background: #d4edda;
  color: #155724;
}

.badge.auto {
  background: #d1ecf1;
  color: #0c5460;
}

.badge.linked {
  background: #f8d7da;
  color: #721c24;
}

.group-description {
  color: #666;
  margin-bottom: 15px;
  line-height: 1.4;
}

.group-theme {
  background: #f8f9fa;
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 15px;
  font-size: 0.9rem;
}

.group-config {
  margin-bottom: 20px;
}

.config-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 0.9rem;
}

.config-label {
  color: #666;
}

.config-value {
  color: #333;
  font-weight: 500;
}

.price-staffel {
  margin-bottom: 20px;
}

.price-staffel h4 {
  margin-bottom: 10px;
  color: #333;
}

.price-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
}

.price-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  font-size: 0.9rem;
}

.group-count {
  color: #666;
}

.price {
  color: #333;
  font-weight: 500;
}

.group-actions,
.subscription-actions {
  display: flex;
  gap: 10px;
}

.subscription-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.subscription-header h3 {
  margin: 0;
  color: #333;
}

.subscription-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.subscription-status.active {
  background: #d4edda;
  color: #155724;
}

.subscription-status.inactive {
  background: #f8d7da;
  color: #721c24;
}

.subscription-details {
  margin-bottom: 20px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.label {
  color: #666;
}

.value {
  color: #333;
  font-weight: 500;
}

.subscription-info {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.subscription-info h4 {
  margin-bottom: 10px;
  color: #333;
}

.subscription-info ul {
  margin: 0;
  padding-left: 20px;
}

.subscription-info li {
  margin-bottom: 5px;
  color: #666;
}

/* Button Styles */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #545b62;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover {
  background: #c82333;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-form {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.form-control:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .signal-groups-page {
    padding: 10px;
  }
  
  .signal-groups-grid,
  .subscriptions-grid,
  .theme-subscriptions-grid {
    grid-template-columns: 1fr;
  }
  
  .info-content {
    grid-template-columns: 1fr;
  }
  
  .group-actions,
  .subscription-actions {
    flex-direction: column;
  }
  
  .price-list {
    grid-template-columns: 1fr;
  }
}

/* Thematische Gruppen Styles */
.themes-section {
  margin: 20px 0;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.themes-section h4 {
  margin-bottom: 15px;
  color: #333;
}

.themes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.theme-card {
  background: white;
  border-radius: 8px;
  padding: 15px;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.theme-card.subscribed {
  border-color: #28a745;
  background: #f8fff9;
}

.theme-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.theme-header h5 {
  margin: 0;
  color: #333;
  font-size: 1rem;
}

.theme-price {
  background: #007bff;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.theme-description {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 15px;
  line-height: 1.4;
}

.theme-status {
  text-align: center;
}

.status.subscribed {
  color: #28a745;
  font-weight: 500;
}

.btn-subscribe {
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-subscribe:hover {
  background: #0056b3;
}

/* Theme Info Styles */
.theme-info {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.theme-info h4 {
  margin-bottom: 10px;
  color: #333;
}

.theme-info p {
  color: #666;
  margin-bottom: 10px;
}

.price-info {
  font-size: 1.1rem;
  color: #007bff;
  font-weight: 500;
}

/* Responsive Design für thematische Gruppen */
@media (max-width: 768px) {
  .themes-grid {
    grid-template-columns: 1fr;
  }
  
  .theme-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style> 