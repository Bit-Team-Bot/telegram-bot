<template>
  <div class="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
    <h2 class="text-2xl font-bold mb-6">Zahlung für {{ package.name }}</h2>
    
    <div class="mb-6">
      <p class="text-gray-600">Preis: {{ package.price }} BUSD</p>
      <p class="text-gray-600">Laufzeit: {{ package.duration_days }} Tage</p>
    </div>
    
    <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
      {{ error }}
    </div>
    
    <form @submit.prevent="submitPayment" class="space-y-4">
      <div>
        <label class="block text-gray-700 mb-2">Transaktions-Hash</label>
        <input
          v-model="txHash"
          type="text"
          required
          class="w-full px-4 py-2 border rounded focus:outline-none focus:border-blue-500"
          placeholder="0x..."
        >
      </div>
      
      <div class="bg-gray-100 p-4 rounded">
        <h3 class="font-bold mb-2">Zahlungsanweisung:</h3>
        <p class="text-sm text-gray-600">
          1. Sende genau {{ package.price }} BUSD an:<br>
          <code class="bg-gray-200 px-2 py-1 rounded">{{ botWallet }}</code>
        </p>
        <p class="text-sm text-gray-600 mt-2">
          2. Füge den Transaktions-Hash oben ein
        </p>
      </div>
      
      <button
        type="submit"
        :disabled="loading"
        class="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
      >
        {{ loading ? 'Wird verarbeitet...' : 'Zahlung bestätigen' }}
      </button>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

export default {
  name: 'PaymentForm',
  
  props: {
    package: {
      type: Object,
      required: true
    }
  },
  
  setup(props) {
    const router = useRouter()
    const txHash = ref('')
    const loading = ref(false)
    const error = ref(null)
    const botWallet = import.meta.env.VITE_BOT_WALLET || '0x...'
    
    const submitPayment = async () => {
      loading.value = true
      error.value = null
      
      try {
        await axios.post('/api/payments', {
          package_id: props.package.id,
          tx_hash: txHash.value
        })
        
        router.push('/packages')
      } catch (err) {
        error.value = err.response?.data?.detail || 'Fehler bei der Zahlungsverarbeitung'
        console.error(err)
      } finally {
        loading.value = false
      }
    }
    
    return {
      txHash,
      loading,
      error,
      botWallet,
      submitPayment
    }
  }
}
</script> 