<template>
  <div class="package-selector">
    <h2 class="headline">Pakete & Signalgruppen</h2>
    <div class="packages">
      <div v-for="(pkg, idx) in packages" :key="pkg.name" class="package-card">
        <h3>{{ pkg.name }}</h3>
        <ul>
          <li v-for="feature in pkg.features" :key="feature">{{ feature }}</li>
        </ul>
        <div class="signal-settings" v-if="pkg.signalOption">
          <label>
            Signalgruppen:
            <input type="number" v-model.number="pkg.signalGroups" min="0" :max="pkg.maxSignals" />
          </label>
        </div>
        <div class="prices">
          <div v-for="price in pkg.pricing" :key="price.months">
            {{ price.months }} Monate:
            <b>{{ price.price }} USDT</b>
            <span v-if="price.discount">({{ price.discount }}% Rabatt)</span>
          </div>
        </div>
        <button class="select-btn" @click="selectPackage(idx)">Auswählen</button>
      </div>
    </div>
    <div v-if="selectedPackage !== null" class="checkout">
      <h4>Checkout für: {{ packages[selectedPackage].name }}</h4>
      <label>
        Zahlungsart:
        <select v-model="selectedPayment">
          <option value="usdt">USDT (empfohlen)</option>
          <option value="btc">BTC</option>
        </select>
      </label>
      <button class="pay-btn" @click="pay">Jetzt bezahlen</button>
    </div>
    <button v-if="showBack" class="back-btn" @click="$emit('back')">Zurück</button>
  </div>
</template>

<script setup>
import { ref } from "vue";
const showBack = defineProps({ showBack: Boolean }).showBack ?? true;

const packages = ref([
  {
    name: "Basic",
    features: ["1 Gruppe", "Basis-Tools", "Standard Support"],
    pricing: [
      { months: 1, price: 15 },
      { months: 3, price: 39, discount: 13 },
      { months: 6, price: 69, discount: 23 },
      { months: 12, price: 119, discount: 34 }
    ],
    signalOption: true,
    maxSignals: 1,
    signalGroups: 1,
  },
  {
    name: "Pro",
    features: ["3 Gruppen", "Krypto-News", "Coin Updates", "Premium Support"],
    pricing: [
      { months: 1, price: 29 },
      { months: 3, price: 75, discount: 14 },
      { months: 6, price: 139, discount: 20 },
      { months: 12, price: 259, discount: 25 }
    ],
    signalOption: true,
    maxSignals: 3,
    signalGroups: 2,
  },
  {
    name: "Expert",
    features: ["5 Gruppen", "Krypto-News", "Signalgruppen", "VIP Support"],
    pricing: [
      { months: 1, price: 45 },
      { months: 3, price: 125, discount: 7 },
      { months: 6, price: 235, discount: 13 },
      { months: 12, price: 399, discount: 26 }
    ],
    signalOption: true,
    maxSignals: 5,
    signalGroups: 3,
  },
  {
    name: "Lifetime",
    features: ["Alle Features", "Unlimitierte Gruppen", "VIP Support", "Lifetime Zugang"],
    pricing: [
      { months: "Lifetime", price: 799, discount: 50 }
    ],
    signalOption: true,
    maxSignals: 10,
    signalGroups: 5,
  }
]);

const selectedPackage = ref(null);
const selectedPayment = ref("usdt");

function selectPackage(idx) {
  selectedPackage.value = idx;
}
function pay() {
  // hier kommt dann deine Payment-Logik rein (API Call, Zahlungs-Split, Weiterleitung)
  alert(`Bezahlung ausgelöst für ${packages.value[selectedPackage.value].name} per ${selectedPayment.value}`);
}
</script>

<!-- Styles werden aus globaler index.css verwendet -->
