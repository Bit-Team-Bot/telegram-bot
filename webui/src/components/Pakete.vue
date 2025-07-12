<template>
  <div class="packages-container">
    <div class="packages-grid">
      <div
        v-for="pkg in packages" 
        :key="pkg.id" 
        class="package-card"
        @click="selectPackage(pkg)"
      >
        <div class="package-header">
          <h3 class="package-name">{{ pkg.name }}</h3>
          <div class="package-price">{{ pkg.price }} USDT</div>
        </div>
        
        <div class="package-details">
          <div class="detail-item">
            <svg class="detail-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
            <span>{{ pkg.duration_days }} Tage</span>
          </div>
          
          <div class="detail-item">
            <svg class="detail-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
            <span>{{ pkg.features.join(', ') }}</span>
        </div>
      </div>

        <button class="select-button">
          Paket auswählen
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
    const response = await fetch('/packages/')
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

<!-- Styles werden aus globaler index.css verwendet -->
