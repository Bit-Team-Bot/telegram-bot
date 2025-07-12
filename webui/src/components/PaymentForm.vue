<template>
  <div class="payment-form-container">
    <div class="payment-form-card">
      <h2 class="payment-form-title">Zahlung bearbeiten</h2>
    
      <form @submit.prevent="handleSubmit" class="payment-form">
        <div class="form-group">
          <label for="amount" class="form-label">Betrag (USDT)</label>
          <input 
            id="amount"
            v-model="form.amount" 
            type="number" 
            step="0.01" 
            required
            class="form-input"
          />
    </div>
    
        <div class="form-group">
          <label for="status" class="form-label">Status</label>
          <select 
            id="status"
            v-model="form.status" 
          required
            class="form-select"
        >
            <option value="pending">Ausstehend</option>
            <option value="completed">Abgeschlossen</option>
            <option value="failed">Fehlgeschlagen</option>
          </select>
      </div>
      
        <div class="form-group">
          <label for="notes" class="form-label">Notizen</label>
          <textarea 
            id="notes"
            v-model="form.notes" 
            rows="3"
            class="form-textarea"
          ></textarea>
      </div>
      
        <button type="submit" class="submit-button" :disabled="loading">
          {{ loading ? 'Speichern...' : 'Speichern' }}
      </button>
    </form>
    </div>
  </div>
</template>

<!-- Styles werden aus globaler index.css verwendet --> 