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

<style scoped>
.ownersettings {
  background: #191c22;
  color: #ffb52a;
  min-height: 100vh;
  padding: 32px 16px 30px 16px;
}
.headline {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 22px;
}
.section {
  background: #232632;
  border-radius: 14px;
  padding: 18px 16px 12px;
  margin-bottom: 24px;
  box-shadow: 0 2px 10px #0007;
}
.section-title {
  color: #ffe199;
  font-size: 1.15rem;
  margin-bottom: 13px;
}
.packages-table {
  width: 100%;
  border-spacing: 0;
  background: #232632;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 13px;
  box-shadow: 0 2px 10px #0006;
}
.packages-table th,
.packages-table td {
  padding: 8px 10px;
  border-bottom: 1px solid #232536;
}
.packages-table th {
  background: #21232b;
  color: #ffe199;
  font-size: 1rem;
  font-weight: bold;
}
.packages-table td {
  background: #232632;
  color: #ffb52a;
  font-size: 1rem;
}
.inp {
  background: #242739;
  color: #ffe199;
  border: 1px solid #3d425c;
  border-radius: 6px;
  padding: 6px 9px;
  font-size: 1rem;
  width: 100%;
}
.inp.short { width: 70px; }
.wallet-row {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
  gap: 7px;
}
.add-btn, .act-btn {
  margin-top: 7px;
  background: #ffb52a;
  color: #232632;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  font-size: 1rem;
  padding: 7px 12px;
  cursor: pointer;
}
.act-btn { padding: 6px 8px; }
.act-btn.danger { background: #e25454; color: #fff; }
.add-btn { margin-bottom: 5px; }
label {
  display: block;
  margin: 7px 0;
  color: #ffe199;
}
input[type="checkbox"] {
  margin-right: 8px;
  accent-color: #ffb52a;
}
.back-btn {
  margin-top: 14px;
  padding: 10px 18px;
  background: #22263b;
  color: #ffb52a;
  border: none;
  border-radius: 10px;
  font-weight: bold;
  font-size: 1.08rem;
  cursor: pointer;
}
</style>
