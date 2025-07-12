<template>
  <div class="dashboard-container">
    <!-- Header Section -->
    <div class="header-section">
      <img src="@/assets/wallstreet-header.png" alt="Wallstreet Crypto Header" class="header-image" />

    </div>
    
    <!-- Main Content -->
    <div class="main-content">
      <div class="package-manager">
        <div class="manager-header">
          <h1 class="manager-title">Paketverwaltung</h1>
          <button @click="showAddPackageModal = true" class="add-button">
            <svg class="button-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            Paket hinzufügen
          </button>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Preis</th>
                <th>Dauer</th>
                <th>Features</th>
                <th>Status</th>
                <th>Aktionen</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="pkg in packages" :key="pkg.id">
                <td>{{ pkg.id }}</td>
                <td>{{ pkg.name }}</td>
                <td>{{ pkg.price }} USDT</td>
                <td>{{ pkg.duration_days }} Tage</td>
                <td>{{ pkg.features.join(', ') }}</td>
                <td>
                  <span :class="['status-badge', pkg.is_active ? 'status-active' : 'status-inactive']">
                    {{ pkg.is_active ? 'Aktiv' : 'Inaktiv' }}
                  </span>
                </td>
                <td>
                  <button @click="editPackage(pkg)" class="action-button edit">Bearbeiten</button>
                  <button @click="togglePackageStatus(pkg)" class="action-button toggle">
                    {{ pkg.is_active ? 'Deaktivieren' : 'Aktivieren' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
          
        <!-- Add Package Modal -->
        <div v-if="showAddPackageModal" class="modal-overlay" @click="showAddPackageModal = false">
          <div class="modal-content" @click.stop>
            <h2 class="modal-title">Paket hinzufügen</h2>
            <form @submit.prevent="addPackage" class="modal-form">
              <div class="form-group">
                <label for="name" class="form-label">Name</label>
                <input
                  id="name"
                  v-model="newPackage.name" 
                  type="text"
                  required
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label for="price" class="form-label">Preis (USDT)</label>
                <input
                  id="price"
                  v-model="newPackage.price" 
                  type="number" 
                  step="0.01"
                  required
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label for="duration" class="form-label">Dauer (Tage)</label>
                <input 
                  id="duration"
                  v-model="newPackage.duration_days" 
                  type="number"
                  required
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label for="features" class="form-label">Features (kommagetrennt)</label>
                <input
                  id="features"
                  v-model="newPackage.features" 
                  type="text"
                  placeholder="Feature1, Feature2, Feature3"
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label class="form-label">Status</label>
                <div class="checkbox-group">
                  <label class="checkbox-label">
                    <input
                      type="checkbox" 
                      v-model="newPackage.is_active"
                      class="checkbox-input"
                    />
                    Aktiv
                  </label>
                </div>
              </div>

              <div class="modal-actions">
                <button type="button" @click="showAddPackageModal = false" class="cancel-button">
                  Abbrechen
                </button>
                <button type="submit" class="submit-button">
                  Hinzufügen
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Edit Package Modal -->
        <div v-if="showEditPackageModal" class="modal-overlay" @click="showEditPackageModal = false">
          <div class="modal-content" @click.stop>
            <h2 class="modal-title">Paket bearbeiten</h2>
            <form @submit.prevent="updatePackage" class="modal-form">
              <div class="form-group">
                <label for="edit-name" class="form-label">Name</label>
                <input
                  id="edit-name"
                  v-model="editingPackage.name" 
                  type="text"
                  required
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label for="edit-price" class="form-label">Preis (USDT)</label>
                <input
                  id="edit-price"
                  v-model="editingPackage.price" 
                  type="number" 
                  step="0.01"
                  required
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label for="edit-duration" class="form-label">Dauer (Tage)</label>
                <input 
                  id="edit-duration"
                  v-model="editingPackage.duration_days" 
                  type="number"
                  required
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label for="edit-features" class="form-label">Features (kommagetrennt)</label>
                <input
                  id="edit-features"
                  v-model="editingPackage.features" 
                  type="text"
                  placeholder="Feature1, Feature2, Feature3"
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label class="form-label">Status</label>
                <div class="checkbox-group">
                  <label class="checkbox-label">
                    <input
                      type="checkbox" 
                      v-model="editingPackage.is_active"
                      class="checkbox-input"
                    />
                    Aktiv
                  </label>
                </div>
              </div>

              <div class="modal-actions">
                <button type="button" @click="showEditPackageModal = false" class="cancel-button">
                  Abbrechen
                </button>
                <button type="submit" class="submit-button">
                  Speichern
                </button>
              </div>
            </form>
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

<script>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useToast } from 'vue-toastification'

export default {
  name: 'PackageManager',
  
  setup() {
    const toast = useToast()
    
    // Tabs
    const activeTab = ref('templates')
    
    // Data
    const packageTemplates = ref([])
    const addons = ref([])
    
    // Template Modals
    const showCreateTemplateModal = ref(false)
    const showEditTemplateModal = ref(false)
    const currentTemplate = ref({
      name: '',
      display_name: '',
      package_type: 'basic',
      monthly_price: null,
      one_time_price: null,
      is_active: true
    })
    
    // Add-on Modals
    const showCreateAddonModal = ref(false)
    const showEditAddonModal = ref(false)
    const currentAddon = ref({
      name: '',
      display_name: '',
      description: '',
      monthly_price: 0,
      one_time_price: null,
      is_active: true
    })

    // Feature Matrix
    const selectedTemplateForFeatures = ref('')
    const featureMatrix = ref({})
    const addonAvailability = ref({})

    // Load Data
    const loadPackageTemplates = async () => {
      try {
        console.log('🔄 Lade Paket-Templates...')
        const response = await axios.get('/api/admin/packages/templates')
        packageTemplates.value = response.data
        console.log('✅ Paket-Templates geladen:', packageTemplates.value.length, 'Templates')
        
        // Zeige Info über geladene Templates
        if (packageTemplates.value.length === 0) {
          toast.warning('Keine Paket-Templates gefunden. Erstelle ein neues Template!')
        } else {
          const activeTemplates = packageTemplates.value.filter(t => t.is_active).length
          toast.success(`${packageTemplates.value.length} Templates geladen (${activeTemplates} aktiv)`)
        }
      } catch (error) {
        console.error('❌ Fehler beim Laden der Paket-Templates:', error)
        if (error.response?.status === 404) {
          toast.error('API-Endpoint nicht gefunden. Prüfe die Backend-Konfiguration.')
        } else if (error.response?.status === 401) {
          toast.error('Nicht autorisiert. Prüfe deine Admin-Berechtigung.')
        } else {
          toast.error(`Fehler beim Laden der Paket-Templates: ${error.response?.data?.detail || error.message}`)
        }
      }
    }

    const loadAddons = async () => {
      try {
        console.log('🔄 Lade Add-ons...')
        const response = await axios.get('/api/admin/packages/addons')
        addons.value = response.data
        console.log('✅ Add-ons geladen:', addons.value.length, 'Add-ons')
        
        // Zeige Info über geladene Add-ons
        if (addons.value.length === 0) {
          toast.info('Keine Add-ons gefunden. Erstelle ein neues Add-on!')
        } else {
          const activeAddons = addons.value.filter(a => a.is_active).length
          toast.success(`${addons.value.length} Add-ons geladen (${activeAddons} aktiv)`)
        }
      } catch (error) {
        console.error('❌ Fehler beim Laden der Add-ons:', error)
        if (error.response?.status === 404) {
          toast.error('API-Endpoint nicht gefunden. Prüfe die Backend-Konfiguration.')
        } else if (error.response?.status === 401) {
          toast.error('Nicht autorisiert. Prüfe deine Admin-Berechtigung.')
        } else {
          toast.error(`Fehler beim Laden der Add-ons: ${error.response?.data?.detail || error.message}`)
        }
      }
    }

    // Template Functions
    const editTemplate = (template) => {
      currentTemplate.value = { ...template }
      showEditTemplateModal.value = true
    }

    const deleteTemplate = async (template) => {
      if (!confirm(`Möchten Sie das Template "${template.display_name}" wirklich löschen?`)) return
      
      try {
        await axios.delete(`/api/admin/packages/templates/${template.id}`)
        await loadPackageTemplates()
        toast.success('Template erfolgreich gelöscht')
      } catch (error) {
        const message = error.response?.data?.detail || 'Fehler beim Löschen des Templates'
        toast.error(message)
        console.error('Fehler beim Löschen des Templates:', error)
      }
    }

    const saveTemplate = async () => {
      try {
        if (showEditTemplateModal.value) {
          await axios.put(`/api/admin/packages/templates/${currentTemplate.value.id}`, currentTemplate.value)
          toast.success('Template erfolgreich aktualisiert')
        } else {
          await axios.post('/api/admin/packages/templates', currentTemplate.value)
          toast.success('Template erfolgreich erstellt')
        }
        await loadPackageTemplates()
        closeTemplateModal()
      } catch (error) {
        const message = error.response?.data?.detail || 'Fehler beim Speichern des Templates'
        toast.error(message)
        console.error('Fehler beim Speichern des Templates:', error)
      }
    }

    const closeTemplateModal = () => {
      showCreateTemplateModal.value = false
      showEditTemplateModal.value = false
      currentTemplate.value = {
        name: '',
        display_name: '',
        package_type: 'basic',
        monthly_price: null,
        one_time_price: null,
        is_active: true
      }
    }

    // Add-on Functions
    const editAddon = (addon) => {
      currentAddon.value = { ...addon }
      showEditAddonModal.value = true
    }

    const deleteAddon = async (addon) => {
      if (!confirm(`Möchten Sie das Add-on "${addon.display_name}" wirklich löschen?`)) return
      
      try {
        await axios.delete(`/api/admin/packages/addons/${addon.id}`)
        await loadAddons()
        toast.success('Add-on erfolgreich gelöscht')
      } catch (error) {
        const message = error.response?.data?.detail || 'Fehler beim Löschen des Add-ons'
        toast.error(message)
        console.error('Fehler beim Löschen des Add-ons:', error)
      }
    }

    const saveAddon = async () => {
      try {
        if (showEditAddonModal.value) {
          await axios.put(`/api/admin/packages/addons/${currentAddon.value.id}`, currentAddon.value)
          toast.success('Add-on erfolgreich aktualisiert')
        } else {
          await axios.post('/api/admin/packages/addons', currentAddon.value)
          toast.success('Add-on erfolgreich erstellt')
        }
        await loadAddons()
        closeAddonModal()
      } catch (error) {
        const message = error.response?.data?.detail || 'Fehler beim Speichern des Add-ons'
        toast.error(message)
        console.error('Fehler beim Speichern des Add-ons:', error)
      }
    }

    const closeAddonModal = () => {
      showCreateAddonModal.value = false
      showEditAddonModal.value = false
      currentAddon.value = {
        name: '',
        display_name: '',
        description: '',
        monthly_price: 0,
        one_time_price: null,
        is_active: true
      }
    }

    // Feature Matrix Functions
    const manageFeatures = async (template) => {
      selectedTemplateForFeatures.value = template.id
      await loadFeatureMatrix(template.id)
    }

    const loadFeatureMatrix = async (templateId) => {
      try {
        const response = await axios.get(`/api/admin/packages/templates/${templateId}/features`)
        featureMatrix.value = response.data.features || {}
        
        // Add-on Verfügbarkeit initialisieren
        addonAvailability.value = {}
        response.data.available_addons?.forEach(addon => {
          addonAvailability.value[addon.id] = addon.is_enabled
        })
        
        console.log('✅ Feature-Matrix geladen:', response.data)
      } catch (error) {
        toast.error('Fehler beim Laden der Feature-Matrix')
        console.error('Fehler beim Laden der Feature-Matrix:', error)
      }
    }

    const saveFeatureMatrix = async () => {
      try {
        // Features speichern
        await axios.put(`/api/admin/packages/templates/${selectedTemplateForFeatures.value}/features`, {
          features: featureMatrix.value
        })
        
        // Add-on Verfügbarkeit speichern
        for (const [addonId, enabled] of Object.entries(addonAvailability.value)) {
          await axios.put(`/api/admin/packages/templates/${selectedTemplateForFeatures.value}/addons/${addonId}`, {
            enabled: enabled
          })
        }
        
        toast.success('Feature-Matrix erfolgreich gespeichert')
      } catch (error) {
        toast.error('Fehler beim Speichern der Feature-Matrix')
        console.error('Fehler beim Speichern der Feature-Matrix:', error)
      }
    }

    const getTemplateName = (templateId) => {
      const template = packageTemplates.value.find(t => t.id === templateId)
      return template ? template.display_name : 'Unbekannt'
    }

    onMounted(() => {
      loadPackageTemplates()
      loadAddons()
    })

    return {
      // Tabs
      activeTab,
      
      // Data
      packageTemplates,
      addons,
      
      // Template Modals
      showCreateTemplateModal,
      showEditTemplateModal,
      currentTemplate,
      
      // Add-on Modals
      showCreateAddonModal,
      showEditAddonModal,
      currentAddon,
      
      // Feature Matrix
      selectedTemplateForFeatures,
      featureMatrix,
      addonAvailability,
      
      // Template Functions
      editTemplate,
      deleteTemplate,
      saveTemplate,
      closeTemplateModal,
      
      // Add-on Functions
      editAddon,
      deleteAddon,
      saveAddon,
      closeAddonModal,
      
      // Feature Matrix Functions
      manageFeatures,
      saveFeatureMatrix,
      getTemplateName
    }
  }
}
</script>

<!-- Styles werden aus globaler index.css verwendet --> 