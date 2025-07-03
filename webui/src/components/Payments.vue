<template>
  <div class="payments">
    <h2>Zahlungen & Status</h2>

    <section v-if="selectedPackage">
      <h3>Gewähltes Paket</h3>
      <div>{{ selectedPackage.name }} — {{ selectedPackage.price_usdt }} USDT ({{ selectedPackage.duration_days > 0 ? selectedPackage.duration_days + ' Tage' : 'Lifetime' }})</div>
      <button @click="payForPackage">Bezahlen</button>
    </section>
    <section v-else>
      <div>Bitte wähle zuerst ein Paket auf der <router-link to="/pakete">Paket-Auswahl</router-link>-Seite.</div>
    </section>

    <section>
      <h3>Deine Zahlungen</h3>
      <!-- Tabelle wie gehabt -->
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const selectedPackageId = ref(localStorage.getItem('selectedPackageId') || null)
const packages = ref([])
const selectedPackage = computed(() => packages.value.find(p => p.id == selectedPackageId.value))
const myPayments = ref([])

const loadPackages = async () => {
  const res = await fetch("https://api.bit-team-bot.online/packages/")
  packages.value = await res.json()
}
const loadMyPayments = async () => {
  const res = await fetch(`https://api.bit-team-bot.online/payments/by_user/${authStore.userId}`)
  myPayments.value = await res.json()
}
const payForPackage = async () => {
  if (!selectedPackage.value) return
  const res = await fetch("https://api.bit-team-bot.online/payments/create", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: authStore.userId, package_id: selectedPackage.value.id })
  })
  if (res.ok) {
    alert("Zahlung erfolgreich angelegt!")
    await loadMyPayments()
  } else {
    const err = await res.json().catch(() => ({}))
    alert("Fehler: " + (err.detail || "Unbekannter Fehler"))
  }
}
onMounted(() => {
  loadPackages()
  loadMyPayments()
})
</script>
