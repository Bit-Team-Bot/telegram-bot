<template>
  <div class="signal-groups-manager">
    <div class="header">
      <h1>Signalgruppen-Verwaltung</h1>
      <p>Verwalte Signalgruppen mit verschiedenen Preis-Staffelungen (1-5 Gruppen)</p>
    </div>

    <!-- Signalgruppen-Tabelle -->
    <div class="section">
      <div class="section-header">
        <h2>Signalgruppen</h2>
        <button @click="showCreateModal = true" class="btn-primary">
          <span class="icon">➕</span>
          Neue Signalgruppe
        </button>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Beschreibung</th>
              <th>Preise (1-5 Gruppen)</th>
              <th>Status</th>
              <th>Aktionen</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="group in signalGroups" :key="group.id" class="hover:bg-gray-50">
              <td class="font-medium">{{ group.name }}</td>
              <td>{{ group.description || "-" }}</td>
              <td class="prices">
                <div class="price-grid">
                  <span class="price-item">1: €{{ group.price_1_group }}</span>
                  <span class="price-item">2: €{{ group.price_2_groups }}</span>
                  <span class="price-item">3: €{{ group.price_3_groups }}</span>
                  <span class="price-item">4: €{{ group.price_4_groups }}</span>
                  <span class="price-item">5: €{{ group.price_5_groups }}</span>
                </div>
              </td>
              <td>
                <span :class="['status-badge', group.is_active ? 'status-active' : 'status-inactive']">
                  {{ group.is_active ? "Aktiv" : "Inaktiv" }}
                </span>
              </td>
              <td class="actions">
                <button @click="editGroup(group)" class="btn-secondary btn-sm">
                  <span class="icon">Bearbeiten</span>
                  Bearbeiten
                </button>
                <button @click="toggleGroup(group)" class="btn-secondary btn-sm">
                  <span class="icon">{{ group.is_active ? "Pause" : "Play" }}</span>
                  {{ group.is_active ? "Deaktivieren" : "Aktivieren" }}
                </button>
                <button @click="deleteGroup(group)" class="btn-danger btn-sm">
                  <span class="icon">Loeschen</span>
                  Loeschen
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal für Erstellen/Bearbeiten -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ showEditModal ? "Signalgruppe bearbeiten" : "Neue Signalgruppe" }}</h3>
          <button @click="closeModal" class="modal-close">×</button>
        </div>
        
        <form @submit.prevent="saveGroup" class="modal-body">
          <div class="form-group">
            <label>Name *</label>
            <input 
              v-model="currentGroup.name" 
              type="text" 
              required 
              placeholder="z.B. BTC-Signale Premium"
            />
          </div>
          
          <div class="form-group">
            <label>Beschreibung</label>
            <textarea 
              v-model="currentGroup.description" 
              rows="3" 
              placeholder="Beschreibung der Signalgruppe..."
            ></textarea>
          </div>
          
          <div class="form-group">
            <label>Preise (€ pro Monat)</label>
            <div class="price-inputs">
              <div class="price-input">
                <label>1 Gruppe:</label>
                <input 
                  v-model.number="currentGroup.price_1_group" 
                  type="number" 
                  step="0.01" 
                  min="0" 
                  required
                />
              </div>
              <div class="price-input">
                <label>2 Gruppen:</label>
                <input 
                  v-model.number="currentGroup.price_2_groups" 
                  type="number" 
                  step="0.01" 
                  min="0" 
                  required
                />
              </div>
              <div class="price-input">
                <label>3 Gruppen:</label>
                <input 
                  v-model.number="currentGroup.price_3_groups" 
                  type="number" 
                  step="0.01" 
                  min="0" 
                  required
                />
              </div>
              <div class="price-input">
                <label>4 Gruppen:</label>
                <input 
                  v-model.number="currentGroup.price_4_groups" 
                  type="number" 
                  step="0.01" 
                  min="0" 
                  required
                />
              </div>
              <div class="price-input">
                <label>5 Gruppen:</label>
                <input 
                  v-model.number="currentGroup.price_5_groups" 
                  type="number" 
                  step="0.01" 
                  min="0" 
                  required
                />
              </div>
            </div>
          </div>
          
          <div class="form-group">
            <label class="checkbox-label">
              <input 
                v-model="currentGroup.is_active" 
                type="checkbox" 
              />
              <span>Aktiv</span>
            </label>
          </div>
          
          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn-secondary">
              Abbrechen
            </button>
            <button type="submit" class="btn-primary">
              {{ showEditModal ? "Aktualisieren" : "Erstellen" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"
import { useToast } from "vue-toastification"

const toast = useToast()

// Reactive data
const signalGroups = ref([])
const showCreateModal = ref(false)
const showEditModal = ref(false)
const currentGroup = ref({
  name: "",
  description: "",
  price_1_group: 0,
  price_2_groups: 0,
  price_3_groups: 0,
  price_4_groups: 0,
  price_5_groups: 0,
  is_active: true
})

// Methods
const loadSignalGroups = async () => {
  try {
    const response = await axios.get("/api/admin/signal-groups")
    signalGroups.value = response.data
    console.log("Signalgruppen geladen:", signalGroups.value.length)
  } catch (error) {
    console.error("Fehler beim Laden der Signalgruppen:", error)
    toast.error("Fehler beim Laden der Signalgruppen")
  }
}

const editGroup = (group) => {
  currentGroup.value = { ...group }
  showEditModal.value = true
}

const toggleGroup = async (group) => {
  try {
    await axios.put(`/api/admin/signal-groups/${group.id}`, {
      is_active: !group.is_active
    })
    group.is_active = !group.is_active
    toast.success(`Signalgruppe ${group.is_active ? "aktiviert" : "deaktiviert"}`)
  } catch (error) {
    console.error("Fehler beim Umschalten der Signalgruppe:", error)
    toast.error("Fehler beim Umschalten der Signalgruppe")
  }
}

const deleteGroup = async (group) => {
  if (!confirm(`Möchtest du die Signalgruppe "${group.name}" wirklich löschen?`)) {
    return
  }
  
  try {
    await axios.delete(`/api/admin/signal-groups/${group.id}`)
    signalGroups.value = signalGroups.value.filter(g => g.id !== group.id)
    toast.success("Signalgruppe erfolgreich gelöscht")
  } catch (error) {
    console.error("Fehler beim Löschen der Signalgruppe:", error)
    toast.error("Fehler beim Löschen der Signalgruppe")
  }
}

const saveGroup = async () => {
  try {
    if (showEditModal.value) {
      await axios.put(`/api/admin/signal-groups/${currentGroup.value.id}`, currentGroup.value)
      toast.success("Signalgruppe erfolgreich aktualisiert")
    } else {
      await axios.post("/api/admin/signal-groups", currentGroup.value)
      toast.success("Signalgruppe erfolgreich erstellt")
    }
    
    closeModal()
    await loadSignalGroups()
  } catch (error) {
    console.error("Fehler beim Speichern der Signalgruppe:", error)
    toast.error("Fehler beim Speichern der Signalgruppe")
  }
}

const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  currentGroup.value = {
    name: "",
    description: "",
    price_1_group: 0,
    price_2_groups: 0,
    price_3_groups: 0,
    price_4_groups: 0,
    price_5_groups: 0,
    is_active: true
  }
}

onMounted(() => {
  loadSignalGroups()
})
</script>

<style scoped>
.signal-groups-manager {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 2rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.header p {
  color: #6b7280;
}

.section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.section-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.prices {
  min-width: 300px;
}

.price-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.5rem;
}

.price-item {
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  text-align: center;
  font-weight: 500;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-active {
  background: #dcfce7;
  color: #166534;
}

.status-inactive {
  background: #fef2f2;
  color: #dc2626;
}

.actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-primary,
.btn-secondary,
.btn-danger {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 500;
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

.icon {
  font-size: 1rem;
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
  border-radius: 8px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.modal-close:hover {
  background: #f3f4f6;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.price-inputs {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
}

.price-input {
  display: flex;
  flex-direction: column;
}

.price-input label {
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.price-input input {
  padding: 0.5rem;
  font-size: 0.875rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  margin: 0;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

/* Responsive */
@media (max-width: 768px) {
  .signal-groups-manager {
    padding: 1rem;
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .price-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .actions {
    flex-direction: column;
  }
  
  .price-inputs {
    grid-template-columns: 1fr;
  }
}
</style>
