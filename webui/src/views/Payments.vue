<template>
  <div class="dashboard-container">
    <!-- Header Section -->
    <div class="header-section">
      <img src="@/assets/wallstreet-header.png" alt="Wallstreet Crypto Header" class="header-image" />
    </div>
    
    <!-- Main Content -->
    <div class="main-content">
      <div class="payments-page">
        <div class="page-header">
          <h1 class="page-title">Zahlungen</h1>
          <p class="page-subtitle">Übersicht über alle Zahlungen und Transaktionen</p>
        </div>

        <div class="overview-grid">
          <div class="overview-card">
            <div class="overview-icon">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
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
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
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
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
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
          <h2 class="section-title">Zahlungshistorie</h2>
          
          <div class="table-container">
            <table class="payments-table">
              <thead>
                <tr>
                  <th>Datum</th>
                  <th>Beschreibung</th>
                  <th>Betrag</th>
                  <th>Status</th>
                  <th>Aktionen</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="payment in payments" :key="payment.id">
                  <td>{{ formatDate(payment.date) }}</td>
                  <td>{{ payment.description }}</td>
                  <td>{{ payment.amount }} €</td>
                  <td>
                    <span :class="['status-badge', getStatusClass(payment.status)]">
                      {{ payment.status }}
                    </span>
                  </td>
                  <td>
                    <button @click="viewPayment(payment)" class="action-button">
                      Details
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Back to Dashboard Section -->
    <div class="back-section">
      <BaseButton @click="$router.push('/dashboard')">
        Zurück zum Dashboard
      </BaseButton>
    </div>
  </div>
</template>

<script setup>
</script>

<!-- Styles werden aus globaler index.css verwendet --> 