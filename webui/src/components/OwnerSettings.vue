<template>
  <div class="ownersettings">
    <h2 class="headline">Owner Settings & Paketverwaltung</h2>

    <section class="section">
      <h3 class="section-title">Pakete verwalten</h3>
      <table class="packages-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Preis (USDT)</th>
            <th>Dauer (Monate)</th>
            <th>Rabatt (%)</th>
            <th>Gruppen</th>
            <th>Signalgruppen</th>
            <th>Aktionen</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(pkg, i) in packages" :key="pkg.id">
            <td><input v-model="pkg.name" class="inp" /></td>
            <td><input type="number" v-model.number="pkg.price" class="inp short" /></td>
            <td><input type="number" v-model.number="pkg.duration" class="inp short" /></td>
            <td><input type="number" v-model.number="pkg.discount" class="inp short" /></td>
            <td><input type="number" v-model.number="pkg.groups" class="inp short" /></td>
            <td><input type="number" v-model.number="pkg.signalgroups" class="inp short" /></td>
            <td>
              <button class="act-btn" @click="savePkg(i)">💾</button>
              <button class="act-btn danger" @click="removePkg(i)">🗑️</button>
            </td>
          </tr>
        </tbody>
      </table>
      <button class="add-btn" @click="addPkg">➕ Neues Paket</button>
    </section>

    <section class="section">
      <h3 class="section-title">Signalgruppen Staffelung & Preise</h3>
      <table class="packages-table">
        <thead>
          <tr>
            <th>Anzahl Signalgruppen</th>
            <th>Preis/Monat (USDT)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(sg, i) in signalStaffel" :key="i">
            <td><input type="number" v-model.number="sg.count" class="inp short" /></td>
            <td><input type="number" v-model.number="sg.price" class="inp short" /></td>
          </tr>
        </tbody>
      </table>
      <button class="add-btn" @click="addSignalStaffel">➕ Neue Staffel</button>
    </section>

    <section class="section">
      <h3 class="section-title">Zahlungsoptionen verwalten</h3>
      <div>
        <label>Exchange Wallet Adressen (wird automatisch aufgeteilt)</label>
        <div v-for="(w, i) in wallets" :key="i" class="wallet-row">
          <input v-model="w.addr" class="inp" placeholder="USDT Wallet Adresse" />
          <button class="act-btn danger" @click="removeWallet(i)">🗑️</button>
        </div>
        <button class="add-btn" @click="addWallet">➕ Neue Wallet</button>
      </div>
    </section>

    <section class="section">
      <h3 class="section-title">Zusatzfunktionen</h3>
      <label>
        <input type="checkbox" v-model="addons.forwardOwnName" />
        Nachrichten im eigenen Namen weiterleiten (extra buchbar)
      </label>
      <label>
        <input type="checkbox" v-model="addons.themeRouting" />
        Themenbasierte Gruppen-Weiterleitung
      </label>
      <label>
        <input type="checkbox" v-model="addons.vipSupport" />
        VIP/Experten Support (extra buchbar)
      </label>
    </section>

    <button class="back-btn" @click="$router.back()">Zurück</button>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue"

// Demo/Defaultdaten, API Anbindung möglich
const packages = reactive([
  { id: 1, name: "Basic", price: 29, duration: 1, discount: 0, groups: 1, signalgroups: 0 },
  { id: 2, name: "Pro", price: 59, duration: 1, discount: 0, groups: 3, signalgroups: 2 },
  { id: 3, name: "Expert", price: 99, duration: 1, discount: 0, groups: 5, signalgroups: 5 },
  { id: 4, name: "Lifetime", price: 499, duration: 999, discount: 15, groups: 7, signalgroups: 7 }
])
function addPkg() {
  packages.push({ id: Date.now(), name: "Neu", price: 0, duration: 1, discount: 0, groups: 1, signalgroups: 0 })
}
function savePkg(i) {
  alert("Gespeichert: " + packages[i].name)
}
function removePkg(i) {
  packages.splice(i, 1)
}

const signalStaffel = reactive([
  { count: 1, price: 20 }, { count: 2, price: 35 }, { count: 3, price: 49 }
])
function addSignalStaffel() {
  signalStaffel.push({ count: 0, price: 0 })
}

const wallets = reactive([
  { addr: "TExch1Abc...1234" }, { addr: "BExch2Zyx...9876" }, { addr: "MExch3Xyz...5678" }
])
function addWallet() { wallets.push({ addr: "" }) }
function removeWallet(i) { wallets.splice(i, 1) }

const addons = reactive({
  forwardOwnName: true,
  themeRouting: true,
  vipSupport: false
})
</script>

<!-- Styles werden aus globaler index.css verwendet -->
