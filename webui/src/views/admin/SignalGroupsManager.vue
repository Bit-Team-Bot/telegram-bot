<template>
  <div class="dashboard-container">
    <!-- Header Section -->
    <div class="header-section">
      <img src="@/assets/wallstreet-header.png" alt="Wallstreet Crypto Header" class="header-image" />

    </div>
    
    <!-- Main Content -->
    <div class="main-content">
      <!-- Page Header (globaler Style) -->
      <div class="page-header">
        <h1 class="page-title">Signalgruppen-Verwaltung</h1>
        <p class="page-subtitle">Verwalte Signalgruppen mit verschiedenen Preis-Staffelungen (1-5 Gruppen)</p>
      </div>

      <!-- User Role Box (Platzhalter für zukünftige Funktionen) -->
      <div class="user-role-box">
        <div class="role-content">
          <!-- Hier können später User Role Funktionen/Boxen eingefügt werden -->
        </div>
      </div>

      <!-- Signalgruppen Cards -->
      <div class="nav-grid">
        <div class="nav-card" v-for="group in signalGroups" :key="group.id">
          <div class="card-icon">
            <span>Signalgruppe</span>
          </div>
          <h3 class="card-title">{{ group.name }}</h3>
          <p class="card-description">{{ group.description || "Keine Beschreibung" }}</p>
          
          <!-- Preise -->
          <div class="price-display">
            <div class="price-item">1: €{{ group.price_1_group }}</div>
            <div class="price-item">2: €{{ group.price_2_groups }}</div>
            <div class="price-item">3: €{{ group.price_3_groups }}</div>
            <div class="price-item">4: €{{ group.price_4_groups }}</div>
            <div class="price-item">5: €{{ group.price_5_groups }}</div>
          </div>
          
          <!-- Status -->
          <div class="status-display">
            <span :class="['status-badge', group.is_active ? 'status-active' : 'status-inactive']">
              {{ group.is_active ? "Aktiv" : "Inaktiv" }}
            </span>
          </div>
          
          <!-- Aktionen -->
          <div class="card-actions">
            <button @click="editGroup(group)" class="role-btn admin">
              <span class="role-icon">✏️</span>
              <span class="role-text">Bearbeiten</span>
            </button>
            <button @click="toggleGroup(group)" class="role-btn partner">
              <span class="role-icon">{{ group.is_active ? "⏸️" : "▶️" }}</span>
              <span class="role-text">{{ group.is_active ? "Deaktivieren" : "Aktivieren" }}</span>
            </button>
            <button @click="deleteGroup(group)" class="logout-btn">
              <span class="logout-icon">🗑️</span>
              <span class="logout-text">Löschen</span>
            </button>
          </div>
        </div>
        
        <!-- Neue Signalgruppe Card -->
        <div class="nav-card add-card" @click="showCreateModal = true">
          <div class="card-icon">
            <span>➕</span>
          </div>
          <h3 class="card-title">Neue Signalgruppe</h3>
          <p class="card-description">Erstelle eine neue Signalgruppe mit Preis-Staffelung</p>
        </div>
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
            <button type="button" @click="closeModal" class="role-btn partner">
              Abbrechen
            </button>
            <button type="submit" class="role-btn admin">
              {{ showEditModal ? "Aktualisieren" : "Erstellen" }}
            </button>
          </div>
        </form>
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
    const response = await axios.get('/admin/signal-groups')
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
    await axios.put(`/admin/signal-groups/${group.id}`, {
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
    await axios.delete(`/admin/signal-groups/${group.id}`)
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
      await axios.put(`/admin/signal-groups/${currentGroup.value.id}`, currentGroup.value)
      toast.success("Signalgruppe erfolgreich aktualisiert")
    } else {
      await axios.post('/admin/signal-groups', currentGroup.value)
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

<!-- TODO: Menüstruktur wie oben beschrieben umbauen. -->
<!-- TODO: Admin-Bereich nur noch nach Klick anzeigen, nicht mehr im Menü. -->
<!-- TODO: Einheitliche Styles für alle Boxen und Buttons laut globaler Klasse verwenden. -->
<!-- TODO: Überprüfe lokale Style-Blöcke in Komponenten und räume sie ggf. auf. -->
