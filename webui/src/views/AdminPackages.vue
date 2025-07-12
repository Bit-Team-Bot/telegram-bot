<template>
  <div class="admin-packages">
    <div class="header">
      <h1>📦 Paketverwaltung</h1>
      <p>Verwalte Pakete und Features mit erweiterbarer Checkbox-Struktur</p>
    </div>

    <!-- Paket-Templates -->
    <div class="section">
      <div class="section-header">
        <h2>Paket-Templates</h2>
        <button @click="showCreateTemplate = true" class="btn-primary">
          <span class="icon">➕</span>
          Neues Template
        </button>
      </div>

      <div class="templates-grid">
        <div 
          v-for="template in packageTemplates" 
          :key="template.id" 
          class="template-card"
          :class="{ 'active': template.is_active }"
        >
          <div class="template-header">
            <h3>{{ template.display_name }}</h3>
            <div class="template-status">
              <span :class="template.is_active ? 'status-active' : 'status-inactive'">
                {{ template.is_active ? 'Aktiv' : 'Inaktiv' }}
              </span>
            </div>
          </div>

          <div class="template-pricing">
            <div v-if="template.monthly_price" class="price monthly">
              <span class="amount">{{ template.monthly_price }}</span>
              <span class="currency">USDT</span>
              <span class="period">/Monat</span>
            </div>
            <div v-if="template.one_time_price" class="price lifetime">
              <span class="amount">{{ template.one_time_price }}</span>
              <span class="currency">USDT</span>
              <span class="period">Einmalig</span>
            </div>
          </div>

          <div class="template-actions">
            <button @click="editTemplate(template)" class="btn-secondary">
              <span class="icon">✏️</span>
              Bearbeiten
            </button>
            <button @click="toggleTemplate(template)" class="btn-secondary">
              <span class="icon">{{ template.is_active ? '⏸️' : '▶️' }}</span>
              {{ template.is_active ? 'Deaktivieren' : 'Aktivieren' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Feature-Matrix -->
    <div class="section">
      <div class="section-header">
        <h2>Feature-Matrix</h2>
        <p>Übersicht aller verfügbaren Features und deren Zuordnung zu Paketen</p>
      </div>

      <div class="feature-matrix">
        <div class="matrix-header">
          <div class="feature-column">Feature</div>
          <div class="package-columns">
            <div 
              v-for="template in packageTemplates" 
              :key="template.id"
              class="package-header"
            >
              {{ template.display_name }}
            </div>
          </div>
        </div>

        <div class="matrix-body">
          <div 
            v-for="(feature, key) in featureMatrix" 
            :key="key"
            class="feature-row"
          >
            <div class="feature-info">
              <div class="feature-name">{{ feature.name }}</div>
              <div class="feature-description">{{ feature.description }}</div>
              <div class="feature-category">{{ feature.category }}</div>
            </div>
            
            <div class="feature-checkboxes">
              <div 
                v-for="template in packageTemplates" 
                :key="template.id"
                class="checkbox-cell"
              >
                <input 
                  type="checkbox" 
                  :id="`${key}-${template.id}`"
                  :checked="getFeatureStatus(template, key)"
                  @change="toggleFeature(template, key, $event.target.checked)"
                  :disabled="!template.is_active"
                />
                <label :for="`${key}-${template.id}`"></label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Addons -->
    <div class="section">
      <div class="section-header">
        <h2>Addons</h2>
        <button @click="showCreateAddon = true" class="btn-primary">
          <span class="icon">➕</span>
          Neues Addon
        </button>
      </div>

      <div class="addons-grid">
        <div 
          v-for="addon in addons" 
          :key="addon.id" 
          class="addon-card"
          :class="{ 'active': addon.is_active }"
        >
          <div class="addon-header">
            <h3>{{ addon.display_name }}</h3>
            <div class="addon-status">
              <span :class="addon.is_active ? 'status-active' : 'status-inactive'">
                {{ addon.is_active ? 'Aktiv' : 'Inaktiv' }}
              </span>
            </div>
          </div>

          <div class="addon-description">
            {{ addon.description }}
          </div>

          <div class="addon-pricing">
            <div v-if="addon.monthly_price" class="price">
              <span class="amount">{{ addon.monthly_price }}</span>
              <span class="currency">USDT</span>
              <span class="period">/Monat</span>
            </div>
            <div v-if="addon.one_time_price" class="price">
              <span class="amount">{{ addon.one_time_price }}</span>
              <span class="currency">USDT</span>
              <span class="period">Einmalig</span>
            </div>
          </div>

          <div class="addon-actions">
            <button @click="editAddon(addon)" class="btn-secondary">
              <span class="icon">✏️</span>
              Bearbeiten
            </button>
            <button @click="toggleAddon(addon)" class="btn-secondary">
              <span class="icon">{{ addon.is_active ? '⏸️' : '▶️' }}</span>
              {{ addon.is_active ? 'Deaktivieren' : 'Aktivieren' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <div v-if="showCreateTemplate" class="modal-overlay" @click="showCreateTemplate = false">
      <div class="modal" @click.stop>
        <h3>Neues Paket-Template erstellen</h3>
        <form @submit.prevent="createTemplate">
          <div class="form-group">
            <label>Name:</label>
            <input v-model="newTemplate.name" type="text" required />
          </div>
          <div class="form-group">
            <label>Display Name:</label>
            <input v-model="newTemplate.display_name" type="text" required />
          </div>
          <div class="form-group">
            <label>Paket-Typ:</label>
            <select v-model="newTemplate.package_type" required>
              <option value="starter">Starter</option>
              <option value="pro">Pro</option>
              <option value="expert">Expert</option>
              <option value="lifetime">Lifetime</option>
            </select>
          </div>
          <div class="form-group">
            <label>Monatspreis (USDT):</label>
            <input v-model="newTemplate.monthly_price" type="number" step="0.01" />
          </div>
          <div class="form-group">
            <label>Einmalpreis (USDT):</label>
            <input v-model="newTemplate.one_time_price" type="number" step="0.01" />
          </div>
          <div class="form-actions">
            <button type="button" @click="showCreateTemplate = false" class="btn-secondary">
              Abbrechen
            </button>
            <button type="submit" class="btn-primary">
              Erstellen
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showCreateAddon" class="modal-overlay" @click="showCreateAddon = false">
      <div class="modal" @click.stop>
        <h3>Neues Addon erstellen</h3>
        <form @submit.prevent="createAddon">
          <div class="form-group">
            <label>Name:</label>
            <input v-model="newAddon.name" type="text" required />
          </div>
          <div class="form-group">
            <label>Display Name:</label>
            <input v-model="newAddon.display_name" type="text" required />
          </div>
          <div class="form-group">
            <label>Beschreibung:</label>
            <textarea v-model="newAddon.description" required></textarea>
          </div>
          <div class="form-group">
            <label>Monatspreis (USDT):</label>
            <input v-model="newAddon.monthly_price" type="number" step="0.01" />
          </div>
          <div class="form-group">
            <label>Einmalpreis (USDT):</label>
            <input v-model="newAddon.one_time_price" type="number" step="0.01" />
          </div>
          <div class="form-actions">
            <button type="button" @click="showCreateAddon = false" class="btn-secondary">
              Abbrechen
            </button>
            <button type="submit" class="btn-primary">
              Erstellen
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../api'

export default {
  name: 'AdminPackages',
  setup() {
    const packageTemplates = ref([])
    const addons = ref([])
    const featureMatrix = ref({})
    const showCreateTemplate = ref(false)
    const showCreateAddon = ref(false)
    
    const newTemplate = ref({
      name: '',
      display_name: '',
      package_type: 'starter',
      monthly_price: null,
      one_time_price: null
    })
    
    const newAddon = ref({
      name: '',
      display_name: '',
      description: '',
      monthly_price: null,
      one_time_price: null
    })

    const loadData = async () => {
      try {
        const [templatesRes, addonsRes] = await Promise.all([
          api.get('/admin/packages/templates'),
          api.get('/admin/packages/addons')
        ])
        
        packageTemplates.value = templatesRes.data
        addons.value = addonsRes.data
        
        // Feature-Matrix aus erstem Template extrahieren
        if (packageTemplates.value.length > 0) {
          const firstTemplate = packageTemplates.value[0]
          if (firstTemplate.features && typeof firstTemplate.features === 'object') {
            featureMatrix.value = firstTemplate.features
          }
        }
      } catch (error) {
        console.error('Fehler beim Laden der Daten:', error)
      }
    }

    const getFeatureStatus = (template, featureKey) => {
      if (template.features && typeof template.features === 'object') {
        return template.features[featureKey] || false
      }
      return false
    }

    const toggleFeature = async (template, featureKey, enabled) => {
      try {
        const updatedFeatures = { ...template.features }
        updatedFeatures[featureKey] = enabled
        
        await api.put(`/admin/packages/templates/${template.id}`, {
          features: updatedFeatures
        })
        
        template.features = updatedFeatures
      } catch (error) {
        console.error('Fehler beim Aktualisieren des Features:', error)
      }
    }

    const toggleTemplate = async (template) => {
      try {
        await api.put(`/admin/packages/templates/${template.id}`, {
          is_active: !template.is_active
        })
        
        template.is_active = !template.is_active
      } catch (error) {
        console.error('Fehler beim Umschalten des Templates:', error)
      }
    }

    const toggleAddon = async (addon) => {
      try {
        await api.put(`/admin/packages/addons/${addon.id}`, {
          is_active: !addon.is_active
        })
        
        addon.is_active = !addon.is_active
      } catch (error) {
        console.error('Fehler beim Umschalten des Addons:', error)
      }
    }

    const createTemplate = async () => {
      try {
        await api.post('/admin/packages/templates', newTemplate.value)
        showCreateTemplate.value = false
        newTemplate.value = {
          name: '',
          display_name: '',
          package_type: 'starter',
          monthly_price: null,
          one_time_price: null
        }
        await loadData()
      } catch (error) {
        console.error('Fehler beim Erstellen des Templates:', error)
      }
    }

    const createAddon = async () => {
      try {
        await api.post('/admin/packages/addons', newAddon.value)
        showCreateAddon.value = false
        newAddon.value = {
          name: '',
          display_name: '',
          description: '',
          monthly_price: null,
          one_time_price: null
        }
        await loadData()
      } catch (error) {
        console.error('Fehler beim Erstellen des Addons:', error)
      }
    }

    const editTemplate = (template) => {
      // TODO: Implementiere Template-Bearbeitung
      console.log('Bearbeite Template:', template)
    }

    const editAddon = (addon) => {
      // TODO: Implementiere Addon-Bearbeitung
      console.log('Bearbeite Addon:', addon)
    }

    onMounted(() => {
      loadData()
    })

    return {
      packageTemplates,
      addons,
      featureMatrix,
      showCreateTemplate,
      showCreateAddon,
      newTemplate,
      newAddon,
      getFeatureStatus,
      toggleFeature,
      toggleTemplate,
      toggleAddon,
      createTemplate,
      createAddon,
      editTemplate,
      editAddon
    }
  }
}
</script>

<style scoped>
.admin-packages {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.header h1 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.header p {
  color: #7f8c8d;
  font-size: 1.1rem;
}

.section {
  margin-bottom: 40px;
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h2 {
  color: #2c3e50;
  margin: 0;
}

.section-header p {
  color: #7f8c8d;
  margin: 8px 0 0 0;
}

.templates-grid, .addons-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.template-card, .addon-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.template-card.active, .addon-card.active {
  border-color: #27ae60;
  background: #f0fff4;
}

.template-card:hover, .addon-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.template-header, .addon-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.template-header h3, .addon-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.status-active {
  background: #27ae60;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.status-inactive {
  background: #e74c3c;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.template-pricing, .addon-pricing {
  margin-bottom: 16px;
}

.price {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 8px;
}

.price.monthly {
  color: #3498db;
}

.price.lifetime {
  color: #e67e22;
}

.amount {
  font-size: 1.5rem;
  font-weight: bold;
}

.currency {
  font-size: 1rem;
  font-weight: 600;
}

.period {
  font-size: 0.9rem;
  color: #7f8c8d;
}

.addon-description {
  color: #7f8c8d;
  margin-bottom: 16px;
  line-height: 1.5;
}

.template-actions, .addon-actions {
  display: flex;
  gap: 8px;
}

.btn-primary, .btn-secondary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #ecf0f1;
  color: #2c3e50;
}

.btn-secondary:hover {
  background: #d5dbdb;
  transform: translateY(-1px);
}

.icon {
  font-size: 1rem;
}

/* Feature Matrix */
.feature-matrix {
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e1e8ed;
}

.matrix-header {
  display: grid;
  grid-template-columns: 2fr repeat(auto-fit, 1fr);
  background: #f8f9fa;
  border-bottom: 2px solid #e1e8ed;
}

.feature-column, .package-header {
  padding: 16px;
  font-weight: 600;
  color: #2c3e50;
  text-align: center;
}

.feature-column {
  text-align: left;
}

.matrix-body {
  max-height: 600px;
  overflow-y: auto;
}

.feature-row {
  display: grid;
  grid-template-columns: 2fr repeat(auto-fit, 1fr);
  border-bottom: 1px solid #e1e8ed;
  transition: background-color 0.3s ease;
}

.feature-row:hover {
  background: #f8f9fa;
}

.feature-info {
  padding: 16px;
}

.feature-name {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
}

.feature-description {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-bottom: 4px;
}

.feature-category {
  color: #95a5a6;
  font-size: 0.8rem;
  text-transform: uppercase;
  font-weight: 600;
}

.feature-checkboxes {
  display: grid;
  grid-template-columns: repeat(auto-fit, 1fr);
}

.checkbox-cell {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
}

.checkbox-cell input[type="checkbox"] {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.checkbox-cell input[type="checkbox"]:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal h3 {
  margin-bottom: 20px;
  color: #2c3e50;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  color: #2c3e50;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
}

.form-group textarea {
  height: 80px;
  resize: vertical;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

/* Responsive */
@media (max-width: 768px) {
  .admin-packages {
    padding: 10px;
  }
  
  .section {
    padding: 16px;
  }
  
  .templates-grid,
  .addons-grid {
    grid-template-columns: 1fr;
  }
  
  .feature-matrix {
    font-size: 0.9rem;
  }
  
  .matrix-header,
  .feature-row {
    grid-template-columns: 1fr;
  }
  
  .feature-checkboxes {
    grid-template-columns: repeat(auto-fit, 1fr);
    margin-top: 8px;
  }
}
</style> 