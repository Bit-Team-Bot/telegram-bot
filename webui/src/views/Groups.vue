<template>
  <div class="groups-container">
    <main class="groups-content">
      <div class="page-header">
        <h1 class="page-title">Trading Groups</h1>
        <p class="page-subtitle">Verwalten Sie Ihre Trading-Gruppen</p>
      </div>

      <div class="groups-grid">
        <div class="group-card">
          <div class="group-header">
            <div class="group-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="var(--accent-orange)"/>
              </svg>
            </div>
            <div class="group-info">
              <h3 class="group-name">Bitcoin Signals</h3>
              <p class="group-status active">Aktiv</p>
            </div>
          </div>
          <div class="group-stats">
            <div class="stat">
              <span class="stat-label">Mitglieder</span>
              <span class="stat-value">1,247</span>
            </div>
            <div class="stat">
              <span class="stat-label">Signale</span>
              <span class="stat-value">89</span>
            </div>
          </div>
          <button class="btn-primary group-button">
            Beitreten
          </button>
        </div>

        <div class="group-card">
          <div class="group-header">
            <div class="group-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="var(--accent-orange)"/>
              </svg>
            </div>
            <div class="group-info">
              <h3 class="group-name">Ethereum Trading</h3>
              <p class="group-status active">Aktiv</p>
            </div>
          </div>
          <div class="group-stats">
            <div class="stat">
              <span class="stat-label">Mitglieder</span>
              <span class="stat-value">892</span>
            </div>
            <div class="stat">
              <span class="stat-label">Signale</span>
              <span class="stat-value">156</span>
            </div>
          </div>
          <button class="btn-primary group-button">
            Beitreten
          </button>
        </div>

        <div class="group-card">
          <div class="group-header">
            <div class="group-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="var(--accent-orange)"/>
              </svg>
            </div>
            <div class="group-info">
              <h3 class="group-name">Altcoin Scanner</h3>
              <p class="group-status inactive">Inaktiv</p>
            </div>
          </div>
          <div class="group-stats">
            <div class="stat">
              <span class="stat-label">Mitglieder</span>
              <span class="stat-value">2,134</span>
            </div>
            <div class="stat">
              <span class="stat-label">Signale</span>
              <span class="stat-value">234</span>
            </div>
          </div>
          <button class="btn-secondary group-button" disabled>
            Nicht verfügbar
          </button>
        </div>

        <div class="group-card">
          <div class="group-header">
            <div class="group-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="var(--accent-orange)"/>
              </svg>
            </div>
            <div class="group-info">
              <h3 class="group-name">DeFi Opportunities</h3>
              <p class="group-status active">Aktiv</p>
            </div>
          </div>
          <div class="group-stats">
            <div class="stat">
              <span class="stat-label">Mitglieder</span>
              <span class="stat-value">567</span>
            </div>
            <div class="stat">
              <span class="stat-label">Signale</span>
              <span class="stat-value">78</span>
            </div>
          </div>
          <button class="btn-primary group-button">
            Beitreten
          </button>
        </div>
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
</script>

<style scoped>
.groups-container {
  min-height: 100vh;
  background-color: var(--bg-primary);
  display: flex;
  flex-direction: column;
}

.groups-content {
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

.groups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 48px;
}

.group-card {
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius);
  padding: 24px;
  box-shadow: var(--shadow-3d);
  transition: transform 0.2s ease;
}

.group-card:hover {
  transform: translateY(-4px);
}

.group-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.group-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 179, 43, 0.1);
  border-radius: 12px;
}

.group-icon svg {
  width: 24px;
  height: 24px;
}

.group-info {
  flex: 1;
}

.group-name {
  font-size: 1.2rem;
  font-weight: bold;
  color: var(--text-white);
  margin: 0 0 4px 0;
}

.group-status {
  font-size: 0.9rem;
  font-weight: 500;
  margin: 0;
}

.group-status.active {
  color: #4ade80;
}

.group-status.inactive {
  color: var(--error-red);
}

.group-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 0.8rem;
  color: var(--text-gray);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 1.2rem;
  font-weight: bold;
  color: var(--text-white);
}

.group-button {
  width: 100%;
  padding: 12px;
  font-size: 1rem;
}

.group-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.back-section {
  text-align: center;
  margin-top: 32px;
}

@media (max-width: 768px) {
  .groups-content {
    padding: 16px;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .page-subtitle {
    font-size: 1rem;
  }
  
  .groups-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .group-card {
    padding: 20px;
  }
  
  .group-stats {
    gap: 16px;
  }
}
</style> 