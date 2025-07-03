<template>
  <div class="min-h-screen bg-gray-100 py-8">
    <div class="max-w-6xl mx-auto px-4">
      <h1 class="text-3xl font-bold text-gray-900 mb-8 text-center">Wähle dein Paket</h1>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="paket in pakete"
        :key="paket.id"
          class="bg-white rounded-lg shadow-lg p-6 cursor-pointer transition-all duration-200 hover:shadow-xl"
          :class="{ 'ring-2 ring-blue-500 bg-blue-50': paket.id === selectedId }"
        @click="selectPackage(paket)"
      >
          <div class="text-center">
            <h2 class="text-xl font-bold text-gray-900 mb-4">{{ paket.name }}</h2>
            <div class="space-y-3 text-gray-600">
              <p class="flex items-center justify-center">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ paket.duration_days > 0 ? paket.duration_days + ' Tage' : 'Lifetime' }}
              </p>
              <p class="text-2xl font-bold text-green-600">
                {{ paket.price_usdt }} USDT
              </p>
              <p class="flex items-center justify-center">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ paket.signals_allowed }} Signale erlaubt
              </p>
            </div>
          </div>
        </div>
      </div>

      <div class="text-center mt-8">
        <button 
          v-if="selectedId" 
          @click="confirmSelection"
          class="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          Auswahl bestätigen
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, inject } from 'vue'
import { useRouter } from 'vue-router'

const store = inject('store')
const router = useRouter()

const pakete = ref([])
const selectedId = ref(localStorage.getItem('selectedPackageId') ? Number(localStorage.getItem('selectedPackageId')) : null)

const fetchPakete = async () => {
  try {
    const response = await fetch('/api/packages/')
    if (response.ok) {
      const data = await response.json()
    pakete.value = data
    } else {
      console.error('Fehler beim Laden der Pakete:', response.status)
    }
  } catch (err) {
    console.error('Fehler beim Laden der Pakete:', err)
  }
}

const selectPackage = (paket) => {
  selectedId.value = paket.id
  localStorage.setItem('selectedPackageId', paket.id.toString())
}

const confirmSelection = () => {
  if (selectedId.value) {
    // Hier könnte die Paket-Auswahl an das Backend gesendet werden
    console.log('Paket ausgewählt:', selectedId.value)
    alert('Paket erfolgreich ausgewählt!')
    router.push('/dashboard')
  }
}

onMounted(() => {
  fetchPakete()
})
</script>

<style scoped>
.pakete-container {
  padding: 40px;
  background: linear-gradient(135deg, #191b23 0%, #232536 60%, #2b3147 100%);
  color: #fff;
  min-height: 100vh;
}

.paket-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
}

.paket-card {
  background: #22263b;
  padding: 20px;
  border-radius: 12px;
  width: 220px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: 0.2s;
}

.paket-card.selected {
  border-color: #ffb32b;
  background: #2e3250;
}

.paket-card:hover {
  transform: scale(1.03);
}

button {
  margin-top: 30px;
  padding: 14px 24px;
  font-size: 1.1rem;
  background: #ffb32b;
  border: none;
  border-radius: 8px;
  color: #000;
  cursor: pointer;
  font-weight: bold;
}
</style>
