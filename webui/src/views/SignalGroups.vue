<template>
  <div class="signal-groups-page">
    <div class="header">
      <h1>Signalgruppen</h1>
      <p>Waehle deine Signalgruppen und die Anzahl der Gruppen (1-5)</p>
    </div>

    <!-- Signalgruppen-Grid -->
    <div class="signal-groups-grid">
      <div 
        v-for="group in signalGroups" 
        :key="group.id" 
        class="signal-group-card"
        :class="{ 'selected': selectedGroups.includes(group.id) }"
      >
        <div class="group-header">
          <h3>{{ group.name }}</h3>
          <p class="description">{{ group.description }}</p>
        </div>
        
        <div class="price-staffel">
          <h4>Preise pro Monat:</h4>
          <div class="price-list">
            <div class="price-item">
              <span class="group-count">1 Gruppe</span>
              <span class="price">€{{ group.price_1_group }}</span>
            </div>
            <div class="price-item">
              <span class="group-count">2 Gruppen</span>
              <span class="price">€{{ group.price_2_groups }}</span>
            </div>
            <div class="price-item">
              <span class="group-count">3 Gruppen</span>
              <span class="price">€{{ group.price_3_groups }}</span>
            </div>
            <div class="price-item">
              <span class="group-count">4 Gruppen</span>
              <span class="price">€{{ group.price_4_groups }}</span>
            </div>
            <div class="price-item">
              <span class="group-count">5 Gruppen</span>
              <span class="price">€{{ group.price_5_groups }}</span>
            </div>
          </div>
        </div>
        
        <div class="group-actions">
          <div class="group-selection">
            <label>Anzahl Gruppen:</label>
            <select v-model="groupSelections[group.id]" @change="updateSelection(group.id)">
              <option value="0">Nicht ausgewaehlt</option>
              <option value="1">1 Gruppe</option>
              <option value="2">2 Gruppen</option>
              <option value="3">3 Gruppen</option>
              <option value="4">4 Gruppen</option>
              <option value="5">5 Gruppen</option>
            </select>
          </div>
          
          <div v-if="groupSelections[group.id] > 0" class="selected-price">
            <span>Preis: €{{ getSelectedPrice(group) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Zusammenfassung -->
    <div v-if="totalPrice > 0" class="summary-section">
      <div class="summary-card">
        <h3>Zusammenfassung</h3>
        <div class="summary-items">
          <div v-for="group in selectedGroupsData" :key="group.id" class="summary-item">
            <span class="item-name">{{ group.name }} ({{ groupSelections[group.id] }} Gruppen)</span>
            <span class="item-price">€{{ getSelectedPrice(group) }}</span>
          </div>
        </div>
        <div class="summary-total">
          <span class="total-label">Gesamtpreis pro Monat:</span>
          <span class="total-price">€{{ totalPrice }}</span>
        </div>
        <button @click="purchaseSignalGroups" class="btn-purchase">
          Signalgruppen kaufen
        </button>
      </div>
    </div>

    <!-- Keine Auswahl -->
    <div v-else class="no-selection">
      <p>Waehle mindestens eine Signalgruppe aus, um fortzufahren.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useToast } from 'vue-toastification'
import { useRouter } from 'vue-router'

const toast = useToast()
const router = useRouter()

// Reactive data
const signalGroups = ref([])
const selectedGroups = ref([])
const groupSelections = ref({})

// Computed properties
const selectedGroupsData = computed(() => {
  return signalGroups.value.filter(group => selectedGroups.value.includes(group.id))
})

const totalPrice = computed(() => {
  return selectedGroupsData.value.reduce((total, group) => {
    return total + getSelectedPrice(group)
  }, 0)
})

// Methods
const loadSignalGroups = async () => {
  try {
    const response = await axios.get('/api/admin/signal-groups')
    signalGroups.value = response.data.filter(group => group.is_active)
    console.log('Signalgruppen geladen:', signalGroups.value.length)
    
    // Initialisiere Auswahl
    signalGroups.value.forEach(group => {
      groupSelections.value[group.id] = 0
    })
  } catch (error) {
    console.error('Fehler beim Laden der Signalgruppen:', error)
    toast.error('Fehler beim Laden der Signalgruppen')
  }
}

const updateSelection = (groupId) => {
  const selection = groupSelections.value[groupId]
  
  if (selection > 0) {
    if (!selectedGroups.value.includes(groupId)) {
      selectedGroups.value.push(groupId)
    }
  } else {
    selectedGroups.value = selectedGroups.value.filter(id => id !== groupId)
  }
}

const getSelectedPrice = (group) => {
  const selection = groupSelections.value[group.id]
  switch (selection) {
    case 1: return group.price_1_group
    case 2: return group.price_2_groups
    case 3: return group.price_3_groups
    case 4: return group.price_4_groups
    case 5: return group.price_5_groups
    default: return 0
  }
}

const purchaseSignalGroups = async () => {
  try {
    const purchaseData = {
      signal_groups: selectedGroupsData.value.map(group => ({
        id: group.id,
        name: group.name,
        group_count: groupSelections.value[group.id],
        price: getSelectedPrice(group)
      })),
      total_price: totalPrice.value
    }
    
    // Hier wuerde die Zahlungslogik implementiert werden
    console.log('Kaufe Signalgruppen:', purchaseData)
    
    // Weiterleitung zur Zahlungsseite
    router.push({
      path: '/payments',
      query: { 
        type: 'signal_groups',
        data: JSON.stringify(purchaseData)
      }
    })
    
    toast.success('Weiterleitung zur Zahlungsseite...')
  } catch (error) {
    console.error('Fehler beim Kauf der Signalgruppen:', error)
    toast.error('Fehler beim Kauf der Signalgruppen')
  }
}

onMounted(() => {
  loadSignalGroups()
})
</script>

<style scoped>
.signal-groups-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 3rem;
}

.header h1 {
  font-size: 2.5rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.header p {
  color: #6b7280;
  font-size: 1.1rem;
}

.signal-groups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.signal-group-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  transition: all 0.3s ease;
  border: 3px solid transparent;
}

.signal-group-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.signal-group-card.selected {
  border-color: #3b82f6;
  background: #f8fafc;
}

.group-header {
  margin-bottom: 1.5rem;
}

.group-header h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.description {
  color: #6b7280;
  line-height: 1.5;
}

.price-staffel {
  margin-bottom: 2rem;
}

.price-staffel h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 1rem;
}

.price-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.price-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.group-count {
  font-weight: 500;
  color: #374151;
}

.price {
  font-weight: 600;
  color: #059669;
  font-size: 1.1rem;
}

.group-actions {
  border-top: 1px solid #e5e7eb;
  padding-top: 1.5rem;
}

.group-selection {
  margin-bottom: 1rem;
}

.group-selection label {
  display: block;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.group-selection select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
  background: white;
  transition: border-color 0.2s;
}

.group-selection select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.selected-price {
  text-align: center;
  padding: 1rem;
  background: #dcfce7;
  border-radius: 6px;
  border: 1px solid #bbf7d0;
}

.selected-price span {
  font-weight: 600;
  color: #166534;
  font-size: 1.1rem;
}

.summary-section {
  position: sticky;
  bottom: 2rem;
  z-index: 10;
}

.summary-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  padding: 2rem;
  max-width: 500px;
  margin: 0 auto;
}

.summary-card h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.5rem;
  text-align: center;
}

.summary-items {
  margin-bottom: 1.5rem;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #e5e7eb;
}

.summary-item:last-child {
  border-bottom: none;
}

.item-name {
  font-weight: 500;
  color: #374151;
}

.item-price {
  font-weight: 600;
  color: #059669;
}

.summary-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-top: 2px solid #e5e7eb;
  margin-top: 1rem;
}

.total-label {
  font-weight: 600;
  color: #1f2937;
  font-size: 1.1rem;
}

.total-price {
  font-weight: 700;
  color: #059669;
  font-size: 1.5rem;
}

.btn-purchase {
  width: 100%;
  background: #3b82f6;
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 1.5rem;
}

.btn-purchase:hover {
  background: #2563eb;
  transform: translateY(-2px);
}

.no-selection {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
  font-size: 1.1rem;
}

/* Responsive */
@media (max-width: 768px) {
  .signal-groups-page {
    padding: 1rem;
  }
  
  .signal-groups-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .signal-group-card {
    padding: 1.5rem;
  }
  
  .summary-card {
    margin: 0 1rem;
  }
}
</style>
