<template>
  <div class="dashboard-container">
    <!-- Obere Topbar mit Logout -->
    <div class="topbar">
      <div class="topbar-content">
        <div class="topbar-spacer"></div>
        <button @click="logout" class="logout-btn">
          Logout
        </button>
      </div>
    </div>

    <!-- Header mit Bitcoin-Bild -->
    <div class="header-section">
      <img src="@/assets/wallstreet-header.png" alt="Wallstreet Crypto Header" class="header-image" />
      <div class="header-text">
        <!-- Titel entfernt, da im Dashboard die Überschrift bleibt -->
        <!-- Admin-Badge für Superuser -->
        <div v-if="authStore.isSuperadmin" class="admin-badge">
          <span class="admin-icon">👑</span>
          <span class="admin-text">Administrator</span>
        </div>
        <!-- Partner-Badge für Partner -->
        <div v-if="authStore.isPartner" class="partner-badge">
          <span class="partner-icon">🤝</span>
          <span class="partner-text">Partner</span>
        </div>
      </div>
    </div>

    <!-- Hauptinhalt -->
    <div class="main-content">
      <!-- Begrüßung -->
      <div class="welcome-section">
        <h2 class="welcome-title">Willkommen bei Wallstreet Crypto</h2>
        <p class="welcome-subtitle">Wählen Sie eine Option aus, um zu beginnen</p>
      </div>

      <!-- Erweiterte Dashboard-Komponente -->
      <div class="enhanced-dashboard">
        <Dashboard />
      </div>

      <!-- Admin-Bereich für Superuser -->
      <div v-if="authStore.isSuperadmin" class="admin-section">
        <h3 class="admin-section-title">🔧 Administrator-Bereich</h3>
        <div class="admin-nav-grid">
          <router-link to="/admin/users" class="admin-nav-button">
            <div class="button-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M16 4C16 2.89 15.11 2 14 2C12.89 2 12 2.89 12 4C12 5.11 12.89 6 14 6C15.11 6 16 5.11 16 4M20 22V16H16.5L15.56 15H8.44L7.5 16H4V22H20M22 22H2V16C2 14.89 2.89 14 4 14H7L8 12H16L17 14H20C21.11 14 22 14.89 22 16V22M10 4C10 2.89 9.11 2 8 2C6.89 2 6 2.89 6 4C6 5.11 6.89 6 8 6C9.11 6 10 5.11 10 4Z" fill="currentColor"/>
              </svg>
            </div>
            <span class="button-text">Benutzer verwalten</span>
          </router-link>

          <router-link to="/admin/packages" class="admin-nav-button">
            <div class="button-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="currentColor"/>
              </svg>
            </div>
            <span class="button-text">Pakete verwalten</span>
          </router-link>

          <router-link to="/admin/partners" class="admin-nav-button">
            <div class="button-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M16 4C16 2.89 15.11 2 14 2C12.89 2 12 2.89 12 4C12 5.11 12.89 6 14 6C15.11 6 16 5.11 16 4M20 22V16H16.5L15.56 15H8.44L7.5 16H4V22H20M22 22H2V16C2 14.89 2.89 14 4 14H7L8 12H16L17 14H20C21.11 14 22 14.89 22 16V22M10 4C10 2.89 9.11 2 8 2C6.89 2 6 2.89 6 4C6 5.11 6.89 6 8 6C9.11 6 10 5.11 10 4Z" fill="currentColor"/>
              </svg>
            </div>
            <span class="button-text">Partner verwalten</span>
          </router-link>

          <router-link to="/monitoring" class="admin-nav-button">
            <div class="button-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 13H7V23H3V13Z" fill="currentColor"/>
                <path d="M10 9H14V23H10V9Z" fill="currentColor"/>
                <path d="M17 5H21V23H17V5Z" fill="currentColor"/>
              </svg>
            </div>
            <span class="button-text">System-Monitoring</span>
          </router-link>
        </div>
      </div>

      <!-- Partner-Bereich für Partner -->
      <div v-if="authStore.isPartner" class="partner-section">
        <h3 class="partner-section-title">🤝 Partner-Bereich</h3>
        <div class="partner-nav-grid">
          <router-link to="/admin/signal-groups" class="partner-nav-button">
            <div class="button-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M16 4C16 2.89 15.11 2 14 2C12.89 2 12 2.89 12 4C12 5.11 12.89 6 14 6C15.11 6 16 5.11 16 4M20 22V16H16.5L15.56 15H8.44L7.5 16H4V22H20M22 22H2V16C2 14.89 2.89 14 4 14H7L8 12H16L17 14H20C21.11 14 22 14.89 22 16V22M10 4C10 2.89 9.11 2 8 2C6.89 2 6 2.89 6 4C6 5.11 6.89 6 8 6C9.11 6 10 5.11 10 4Z" fill="currentColor"/>
              </svg>
            </div>
            <span class="button-text">Signal-Gruppen verwalten</span>
          </router-link>

          <router-link to="/admin/payments" class="partner-nav-button">
            <div class="button-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 4H4C2.89 4 2 4.89 2 6V18C2 19.11 2.89 20 4 20H20C21.11 20 22 19.11 22 18V6C22 4.89 21.11 4 20 4M20 18H4V12H20V18M20 8H4V6H20V8M14 16H6V14H14V16Z" fill="currentColor"/>
              </svg>
            </div>
            <span class="button-text">Zahlungen einsehen</span>
          </router-link>

          <router-link to="/admin/statistics" class="partner-nav-button">
            <div class="button-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 13H7V23H3V13Z" fill="currentColor"/>
                <path d="M10 9H14V23H10V9Z" fill="currentColor"/>
                <path d="M17 5H21V23H17V5Z" fill="currentColor"/>
              </svg>
            </div>
            <span class="button-text">Statistiken</span>
          </router-link>

          <router-link to="/admin/features" class="partner-nav-button">
            <div class="button-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="currentColor"/>
              </svg>
            </div>
            <span class="button-text">Features verwalten</span>
          </router-link>
        </div>
      </div>

      <!-- Navigation Grid -->
      <div class="nav-grid">
        <router-link to="/dashboard" class="nav-button">
          <div class="button-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 13H7V23H3V13Z" fill="currentColor"/>
              <path d="M10 9H14V23H10V9Z" fill="currentColor"/>
              <path d="M17 5H21V23H17V5Z" fill="currentColor"/>
            </svg>
          </div>
          <span class="button-text">Dashboard</span>
        </router-link>

        <router-link to="/packages" class="nav-button">
          <div class="button-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="currentColor"/>
            </svg>
          </div>
          <span class="button-text">Pakete</span>
        </router-link>

        <router-link to="/groups" class="nav-button">
          <div class="button-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M16 4C16 2.89 15.11 2 14 2C12.89 2 12 2.89 12 4C12 5.11 12.89 6 14 6C15.11 6 16 5.11 16 4M20 22V16H16.5L15.56 15H8.44L7.5 16H4V22H20M22 22H2V16C2 14.89 2.89 14 4 14H7L8 12H16L17 14H20C21.11 14 22 14.89 22 16V22M10 4C10 2.89 9.11 2 8 2C6.89 2 6 2.89 6 4C6 5.11 6.89 6 8 6C9.11 6 10 5.11 10 4Z" fill="currentColor"/>
            </svg>
          </div>
          <span class="button-text">Groups</span>
        </router-link>

        <router-link to="/payments" class="nav-button">
          <div class="button-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M20 4H4C2.89 4 2 4.89 2 6V18C2 19.11 2.89 20 4 20H20C21.11 20 22 19.11 22 18V6C22 4.89 21.11 4 20 4M20 18H4V12H20V18M20 8H4V6H20V8M14 16H6V14H14V16Z" fill="currentColor"/>
            </svg>
          </div>
          <span class="button-text">Payments</span>
        </router-link>

        <router-link to="/signal-groups" class="nav-button">
          <div class="button-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M16 4C16 2.89 15.11 2 14 2C12.89 2 12 2.89 12 4C12 5.11 12.89 6 14 6C15.11 6 16 5.11 16 4M20 22V16H16.5L15.56 15H8.44L7.5 16H4V22H20M22 22H2V16C2 14.89 2.89 14 4 14H7L8 12H16L17 14H20C21.11 14 22 14.89 22 16V22M10 4C10 2.89 9.11 2 8 2C6.89 2 6 2.89 6 4C6 5.11 6.89 6 8 6C9.11 6 10 5.11 10 4Z" fill="currentColor"/>
            </svg>
          </div>
          <span class="button-text">Signalgruppen</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Dashboard from '../components/Dashboard.vue'

const router = useRouter()
const authStore = useAuthStore()

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background: #0A0A0A;
  display: flex;
  flex-direction: column;
  align-items: center;
  color: white;
}

/* Topbar */
.topbar {
  width: 100%;
  background: #0A0A0A;
  padding: 16px;
  position: sticky;
  top: 0;
  z-index: 10;
}

.topbar-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.topbar-spacer {
  flex: 1;
}

.logout-btn {
  background: transparent;
  color: #FFA726;
  border: 1px solid #FFA726;
  border-radius: 9999px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-right: 16px;
  margin-top: 8px;
}

.logout-btn:hover {
  background: #FFA726;
  color: #000000;
  transform: translateY(-1px);
}

/* Header Section */
.header-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 16px;
  margin-bottom: 32px;
}

.header-image {
  width: 100%;
  max-width: 600px;
  height: auto;
  object-fit: cover;
  border-radius: 16px;
  margin-bottom: 16px;
}

.header-text {
  text-align: center;
}

.main-title {
  font-size: 3rem;
  font-weight: 900;
  color: #FFA726;
  margin: 0 0 8px 0;
  text-shadow: 0 0 20px rgba(255, 167, 38, 0.5);
  letter-spacing: 2px;
}

.subtitle {
  font-size: 1.2rem;
  color: #CCCCCC;
  margin: 0;
  font-weight: 300;
}

/* Main Content */
.main-content {
  width: 100%;
  max-width: 1200px;
  padding: 0 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* Welcome Section */
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

/* Enhanced Dashboard Section */
.enhanced-dashboard {
  width: 100%;
  margin-bottom: 48px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 24px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 167, 38, 0.2);
}

/* Admin Section */
.admin-section {
  width: 100%;
  margin-bottom: 48px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 24px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 167, 38, 0.2);
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

/* Partner Badge */
.partner-badge {
  display: inline-flex;
  align-items: center;
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: #ffffff;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
  margin-top: 8px;
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.partner-icon {
  margin-right: 6px;
  font-size: 1.1rem;
}

.partner-text {
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.admin-section-title {
  font-size: 2rem;
  font-weight: 700;
  color: #FFA726;
  margin-bottom: 24px;
}

.admin-nav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
  width: 100%;
  max-width: 800px;
}

.admin-nav-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(255, 167, 38, 0.1) 0%, rgba(255, 167, 38, 0.05) 100%);
  border: 2px solid rgba(255, 167, 38, 0.3);
  border-radius: 16px;
  padding: 32px 24px;
  text-decoration: none;
  color: #FFA726;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.admin-nav-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 167, 38, 0.1), transparent);
  transition: left 0.5s;
}

.admin-nav-button:hover::before {
  left: 100%;
}

.admin-nav-button:hover {
  transform: translateY(-4px);
  border-color: #FFA726;
  box-shadow: 0 8px 25px rgba(255, 167, 38, 0.3);
  background: linear-gradient(135deg, rgba(255, 167, 38, 0.2) 0%, rgba(255, 167, 38, 0.1) 100%);
}

.button-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 167, 38, 0.1);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.admin-nav-button:hover .button-icon {
  background: rgba(255, 167, 38, 0.2);
  transform: scale(1.1);
}

.button-icon svg {
  width: 24px;
  height: 24px;
  color: #FFA726;
}

.button-text {
  font-size: 1.1rem;
  font-weight: 600;
  text-align: center;
  color: #FFA726;
  transition: all 0.3s ease;
}

.admin-nav-button:hover .button-text {
  color: #ffffff;
}

/* Partner Section */
.partner-section {
  width: 100%;
  margin-bottom: 48px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 24px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 167, 38, 0.2);
}

.partner-section-title {
  font-size: 2rem;
  font-weight: 700;
  color: #FFA726;
  margin-bottom: 24px;
}

.partner-nav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
  width: 100%;
  max-width: 800px;
}

.partner-nav-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(255, 167, 38, 0.1) 0%, rgba(255, 167, 38, 0.05) 100%);
  border: 2px solid rgba(255, 167, 38, 0.3);
  border-radius: 16px;
  padding: 32px 24px;
  text-decoration: none;
  color: #FFA726;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.partner-nav-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 167, 38, 0.1), transparent);
  transition: left 0.5s;
}

.partner-nav-button:hover::before {
  left: 100%;
}

.partner-nav-button:hover {
  transform: translateY(-4px);
  border-color: #FFA726;
  box-shadow: 0 8px 25px rgba(255, 167, 38, 0.3);
  background: linear-gradient(135deg, rgba(255, 167, 38, 0.2) 0%, rgba(255, 167, 38, 0.1) 100%);
}

.button-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 167, 38, 0.1);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.partner-nav-button:hover .button-icon {
  background: rgba(255, 167, 38, 0.2);
  transform: scale(1.1);
}

.button-icon svg {
  width: 24px;
  height: 24px;
  color: #FFA726;
}

.button-text {
  font-size: 1.1rem;
  font-weight: 600;
  text-align: center;
  color: #FFA726;
  transition: all 0.3s ease;
}

.partner-nav-button:hover .button-text {
  color: #ffffff;
}

/* Navigation Grid */
.nav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
  width: 100%;
  max-width: 800px;
  margin-top: 32px;
}

.nav-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(255, 167, 38, 0.1) 0%, rgba(255, 167, 38, 0.05) 100%);
  border: 2px solid rgba(255, 167, 38, 0.3);
  border-radius: 16px;
  padding: 32px 24px;
  text-decoration: none;
  color: #FFA726;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.nav-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 167, 38, 0.1), transparent);
  transition: left 0.5s;
}

.nav-button:hover::before {
  left: 100%;
}

.nav-button:hover {
  transform: translateY(-4px);
  border-color: #FFA726;
  box-shadow: 0 8px 25px rgba(255, 167, 38, 0.3);
  background: linear-gradient(135deg, rgba(255, 167, 38, 0.2) 0%, rgba(255, 167, 38, 0.1) 100%);
}

.button-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 167, 38, 0.1);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.nav-button:hover .button-icon {
  background: rgba(255, 167, 38, 0.2);
  transform: scale(1.1);
}

.button-icon svg {
  width: 24px;
  height: 24px;
  color: #FFA726;
}

.button-text {
  font-size: 1.1rem;
  font-weight: 600;
  text-align: center;
  color: #FFA726;
  transition: all 0.3s ease;
}

.nav-button:hover .button-text {
  color: #ffffff;
}

/* Responsive Design */
@media (max-width: 768px) {
  .main-title {
    font-size: 2rem;
  }
  
  .welcome-title {
    font-size: 2rem;
  }
  
  .nav-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .nav-button {
    padding: 24px 16px;
  }
  
  .enhanced-dashboard {
    padding: 16px;
    margin-bottom: 32px;
  }
}

@media (max-width: 480px) {
  .main-title {
    font-size: 1.5rem;
  }
  
  .welcome-title {
    font-size: 1.5rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }
  
  .welcome-subtitle {
    font-size: 1rem;
  }
}
</style>
