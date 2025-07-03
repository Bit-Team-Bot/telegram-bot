<template>
  <div class="payments-container">
    <main class="payments-content">
      <div class="page-header">
        <h1 class="page-title">Zahlungen</h1>
        <p class="page-subtitle">Verwalten Sie Ihre Zahlungen und Abonnements</p>
      </div>

      <div class="payments-overview">
        <div class="overview-card">
          <div class="overview-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="var(--accent-orange)"/>
            </svg>
          </div>
          <div class="overview-content">
            <h3 class="overview-title">Aktuelles Paket</h3>
            <p class="overview-value">Pro Plan</p>
            <p class="overview-subtitle">€299 / 90 Tage</p>
          </div>
        </div>

        <div class="overview-card">
          <div class="overview-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M20 4H4C2.89 4 2 4.89 2 6V18C2 19.11 2.89 20 4 20H20C21.11 20 22 19.11 22 18V6C22 4.89 21.11 4 20 4M20 18H4V12H20V18M20 8H4V6H20V8M14 16H6V14H14V16Z" fill="var(--accent-orange)"/>
            </svg>
          </div>
          <div class="overview-content">
            <h3 class="overview-title">Nächste Zahlung</h3>
            <p class="overview-value">15. März 2024</p>
            <p class="overview-subtitle">€299.00</p>
          </div>
        </div>

        <div class="overview-card">
          <div class="overview-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M16 4C16 2.89 15.11 2 14 2C12.89 2 12 2.89 12 4C12 5.11 12.89 6 14 6C15.11 6 16 5.11 16 4M20 22V16H16.5L15.56 15H8.44L7.5 16H4V22H20M22 22H2V16C2 14.89 2.89 14 4 14H7L8 12H16L17 14H20C21.11 14 22 14.89 22 16V22M10 4C10 2.89 9.11 2 8 2C6.89 2 6 2.89 6 4C6 5.11 6.89 6 8 6C9.11 6 10 5.11 10 4Z" fill="var(--accent-orange)"/>
            </svg>
          </div>
          <div class="overview-content">
            <h3 class="overview-title">Gesamtausgaben</h3>
            <p class="overview-value">€1,497.00</p>
            <p class="overview-subtitle">5 Zahlungen</p>
          </div>
        </div>
      </div>

      <div class="payments-section">
        <h2 class="section-title">Zahlungsverlauf</h2>
        
        <div class="payments-table">
          <div class="table-header">
            <div class="table-cell">Datum</div>
            <div class="table-cell">Paket</div>
            <div class="table-cell">Betrag</div>
            <div class="table-cell">Status</div>
          </div>
          
          <div class="table-row">
            <div class="table-cell">15. Dez 2023</div>
            <div class="table-cell">Pro Plan</div>
            <div class="table-cell">€299.00</div>
            <div class="table-cell">
              <span class="status-badge success">Bezahlt</span>
            </div>
          </div>
          
          <div class="table-row">
            <div class="table-cell">15. Sep 2023</div>
            <div class="table-cell">Pro Plan</div>
            <div class="table-cell">€299.00</div>
            <div class="table-cell">
              <span class="status-badge success">Bezahlt</span>
            </div>
          </div>
          
          <div class="table-row">
            <div class="table-cell">15. Jun 2023</div>
            <div class="table-cell">Basic Plan</div>
            <div class="table-cell">€99.00</div>
            <div class="table-cell">
              <span class="status-badge success">Bezahlt</span>
            </div>
          </div>
          
          <div class="table-row">
            <div class="table-cell">15. Mär 2023</div>
            <div class="table-cell">Basic Plan</div>
            <div class="table-cell">€99.00</div>
            <div class="table-cell">
              <span class="status-badge success">Bezahlt</span>
            </div>
          </div>
          
          <div class="table-row">
            <div class="table-cell">15. Dez 2022</div>
            <div class="table-cell">Basic Plan</div>
            <div class="table-cell">€99.00</div>
            <div class="table-cell">
              <span class="status-badge success">Bezahlt</span>
            </div>
          </div>
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
.payments-container {
  min-height: 100vh;
  background-color: var(--bg-primary);
  display: flex;
  flex-direction: column;
}

.payments-content {
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

.payments-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 48px;
}

.overview-card {
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--shadow-3d);
  transition: transform 0.2s ease;
}

.overview-card:hover {
  transform: translateY(-2px);
}

.overview-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 179, 43, 0.1);
  border-radius: 12px;
}

.overview-icon svg {
  width: 24px;
  height: 24px;
}

.overview-content {
  flex: 1;
}

.overview-title {
  color: var(--text-gray);
  font-size: 0.9rem;
  font-weight: 500;
  margin: 0 0 4px 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.overview-value {
  color: var(--text-white);
  font-size: 1.3rem;
  font-weight: bold;
  margin: 0 0 4px 0;
}

.overview-subtitle {
  color: var(--text-gray);
  font-size: 0.9rem;
  margin: 0;
}

.payments-section {
  margin-bottom: 48px;
}

.section-title {
  font-size: 1.8rem;
  font-weight: bold;
  color: var(--text-white);
  margin: 0 0 24px 0;
}

.payments-table {
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: var(--shadow-3d);
}

.table-header {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  background-color: rgba(255, 179, 43, 0.1);
  padding: 16px 24px;
  font-weight: bold;
  color: var(--text-white);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.table-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  padding: 16px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: background-color 0.2s ease;
}

.table-row:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.table-row:last-child {
  border-bottom: none;
}

.table-cell {
  color: var(--text-white);
  display: flex;
  align-items: center;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.success {
  background-color: rgba(74, 222, 128, 0.2);
  color: #4ade80;
}

.back-section {
  text-align: center;
  margin-top: 32px;
}

@media (max-width: 768px) {
  .payments-content {
    padding: 16px;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .page-subtitle {
    font-size: 1rem;
  }
  
  .payments-overview {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .overview-card {
    padding: 20px;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: 8px;
    padding: 12px 16px;
  }
  
  .table-cell {
    font-size: 0.9rem;
  }
  
  .table-cell:before {
    content: attr(data-label);
    font-weight: bold;
    color: var(--text-gray);
    margin-right: 8px;
  }
}
</style> 