<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Zurück-Button und Header -->
    <div class="flex items-center justify-between mb-8">
      <div class="flex items-center space-x-4">
        <button
          @click="$router.push('/dashboard')"
          class="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
          </svg>
          <span>Zurück zum Dashboard</span>
        </button>
        <h1 class="text-2xl font-bold">Paket-System verwalten</h1>
      </div>
      
      <div class="flex space-x-4">
        <button
          @click="activeTab = 'templates'"
          :class="['px-4 py-2 rounded transition-colors', activeTab === 'templates' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300']"
        >
          Paket-Templates
        </button>
        <button
          @click="activeTab = 'addons'"
          :class="['px-4 py-2 rounded transition-colors', activeTab === 'addons' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300']"
        >
          Add-ons
        </button>
        <button
          @click="activeTab = 'features'"
          :class="['px-4 py-2 rounded transition-colors', activeTab === 'features' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300']"
        >
          Feature-Matrix
        </button>
      </div>
    </div>

    <!-- Paket-Templates Tab -->
    <div v-if="activeTab === 'templates'" class="space-y-6">
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold">Paket-Templates</h2>
        <button
          @click="showCreateTemplateModal = true"
          class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors"
        >
          Neues Template
        </button>
      </div>

      <!-- Template-Tabelle mit verbesserter Darstellung -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Typ</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Preise</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Aktionen</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="template in packageTemplates" :key="template.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div>
                  <div class="font-medium text-gray-900">{{ template.display_name }}</div>
                  <div class="text-sm text-gray-500">{{ template.name }}</div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                  {{ template.package_type }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm">
                  <div v-if="template.monthly_price">Monatlich: €{{ template.monthly_price }}</div>
                  <div v-if="template.one_time_price">Einmalig: €{{ template.one_time_price }}</div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="['px-2 py-1 rounded-full text-xs', template.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800']">
                  {{ template.is_active ? 'Aktiv' : 'Inaktiv' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  @click="editTemplate(template)"
                  class="text-blue-600 hover:text-blue-900 mr-3 transition-colors"
                >
                  Bearbeiten
                </button>
                <button
                  @click="manageFeatures(template)"
                  class="text-green-600 hover:text-green-900 mr-3 transition-colors"
                >
                  Features
                </button>
                <button
                  @click="deleteTemplate(template)"
                  class="text-red-600 hover:text-red-900 transition-colors"
                >
                  Löschen
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add-ons Tab -->
    <div v-if="activeTab === 'addons'" class="space-y-6">
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold">Add-ons</h2>
        <button
          @click="showCreateAddonModal = true"
          class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Neues Add-on
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="addon in addons" :key="addon.id" class="bg-white rounded-lg shadow p-6">
          <div class="flex justify-between items-start mb-4">
            <div>
              <h3 class="font-medium text-gray-900">{{ addon.display_name }}</h3>
              <p class="text-sm text-gray-500">{{ addon.name }}</p>
            </div>
            <span :class="['px-2 py-1 rounded-full text-xs', addon.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800']">
              {{ addon.is_active ? 'Aktiv' : 'Inaktiv' }}
            </span>
          </div>
          
          <p class="text-sm text-gray-600 mb-4">{{ addon.description }}</p>
          
          <div class="text-sm text-gray-500 mb-4">
            <div v-if="addon.monthly_price">Monatlich: €{{ addon.monthly_price }}</div>
            <div v-if="addon.one_time_price">Einmalig: €{{ addon.one_time_price }}</div>
          </div>

          <div v-if="addon.tiers && addon.tiers.length > 0" class="mb-4">
            <h4 class="font-medium text-sm mb-2">Tiers:</h4>
            <div class="space-y-1">
              <div v-for="tier in addon.tiers" :key="tier.id" class="text-xs text-gray-500">
                {{ tier.level }}: €{{ tier.price }} - {{ tier.description }}
              </div>
            </div>
          </div>

          <div class="flex space-x-2">
            <button
              @click="editAddon(addon)"
              class="text-blue-600 hover:text-blue-900 text-sm"
            >
              Bearbeiten
            </button>
            <button
              @click="deleteAddon(addon)"
              class="text-red-600 hover:text-red-900 text-sm"
            >
              Löschen
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Feature-Matrix Tab -->
    <div v-if="activeTab === 'features'" class="space-y-6">
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold">Feature-Matrix</h2>
        <select v-model="selectedTemplateForFeatures" class="border border-gray-300 rounded px-3 py-2">
          <option value="">Template auswählen</option>
          <option v-for="template in packageTemplates" :key="template.id" :value="template.id">
            {{ template.display_name }}
          </option>
        </select>
      </div>

      <div v-if="selectedTemplateForFeatures" class="bg-white rounded-lg shadow p-6">
        <h3 class="font-medium mb-4">Features für {{ getTemplateName(selectedTemplateForFeatures) }}</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="(value, key) in featureMatrix" :key="key" class="flex items-center">
            <input
              :id="'feature-' + key"
              v-model="featureMatrix[key]"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            >
            <label :for="'feature-' + key" class="ml-2 block text-sm text-gray-900">
              {{ key }}
            </label>
          </div>
        </div>

        <div class="mt-6">
          <h4 class="font-medium mb-2">Verfügbare Add-ons:</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="addon in addons" :key="addon.id" class="flex items-center">
              <input
                :id="'addon-' + addon.id"
                v-model="addonAvailability[addon.id]"
                type="checkbox"
                class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
              >
              <label :for="'addon-' + addon.id" class="ml-2 block text-sm text-gray-900">
                {{ addon.display_name }}
              </label>
            </div>
          </div>
        </div>

        <div class="mt-6 flex justify-end">
          <button
            @click="saveFeatureMatrix"
            class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Feature-Matrix speichern
          </button>
        </div>
      </div>
    </div>

    <!-- Template Modal -->
    <div v-if="showCreateTemplateModal || showEditTemplateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 w-full max-w-2xl">
        <h2 class="text-xl font-bold mb-4">
          {{ showEditTemplateModal ? 'Template bearbeiten' : 'Neues Template' }}
        </h2>

        <form @submit.prevent="saveTemplate" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Name (Code)</label>
            <input
              v-model="currentTemplate.name"
              type="text"
              required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">Anzeigename</label>
            <input
              v-model="currentTemplate.display_name"
              type="text"
              required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">Paket-Typ</label>
            <select
              v-model="currentTemplate.package_type"
              required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="basic">Basic</option>
              <option value="advanced">Advanced</option>
              <option value="pro">Pro</option>
              <option value="lifetime">Lifetime</option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-4">
          <div>
              <label class="block text-sm font-medium text-gray-700">Monatspreis (€)</label>
              <input
                v-model="currentTemplate.monthly_price"
                type="number"
                step="0.01"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Einmalpreis (€)</label>
                <input
                v-model="currentTemplate.one_time_price"
                type="number"
                step="0.01"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">Status</label>
            <select
              v-model="currentTemplate.is_active"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option :value="true">Aktiv</option>
              <option :value="false">Inaktiv</option>
            </select>
          </div>

          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="closeTemplateModal"
              class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Abbrechen
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Speichern
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Add-on Modal -->
    <div v-if="showCreateAddonModal || showEditAddonModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 w-full max-w-2xl">
        <h2 class="text-xl font-bold mb-4">
          {{ showEditAddonModal ? 'Add-on bearbeiten' : 'Neues Add-on' }}
        </h2>

        <form @submit.prevent="saveAddon" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Name (Code)</label>
            <input
              v-model="currentAddon.name"
              type="text"
              required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">Anzeigename</label>
            <input
              v-model="currentAddon.display_name"
              type="text"
              required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">Beschreibung</label>
            <textarea
              v-model="currentAddon.description"
              rows="3"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            ></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Monatspreis (€)</label>
              <input
                v-model="currentAddon.monthly_price"
                type="number"
                step="0.01"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Einmalpreis (€)</label>
              <input
                v-model="currentAddon.one_time_price"
                type="number"
                step="0.01"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">Status</label>
            <select
              v-model="currentAddon.is_active"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option :value="true">Aktiv</option>
              <option :value="false">Inaktiv</option>
            </select>
          </div>

          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="closeAddonModal"
              class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Abbrechen
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Speichern
            </button>
          </div>
        </form>
      </div>
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