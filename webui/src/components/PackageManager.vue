<template>
  <div class="package-manager">
    <h1>Paketverwaltung</h1>
    <button @click="openDialog()">+ Paket hinzufügen</button>
    <table>
      <tr>
        <th>Name</th><th>Gruppen</th><th>Signalgruppen</th><th>Features</th><th>Laufzeiten/Preise</th><th>Aktion</th>
      </tr>
      <tr v-for="pkg in packages" :key="pkg.id">
        <td>{{ pkg.name }}</td>
        <td>{{ pkg.groupLimit }}</td>
        <td>{{ pkg.signalGroups.join(', ') }}</td>
        <td>{{ pkg.features.join(', ') }}</td>
        <td>
          <div v-for="d in pkg.durations" :key="d.months">
            {{ d.months }}M: {{ d.price }} USDT (Rabatt: {{ d.discount }}%)
          </div>
        </td>
        <td>
          <button @click="edit(pkg)">Edit</button>
          <button @click="del(pkg)">Löschen</button>
        </td>
      </tr>
    </table>
    <!-- Paket-Dialog -->
    <dialog v-if="editing">
      <form @submit.prevent="save">
        <input v-model="editing.name" placeholder="Paketname" required/>
        <input type="number" v-model="editing.groupLimit" min="1" placeholder="Gruppenlimit"/>
        <label>Signalgruppen:</label>
        <select v-model="editing.signalGroups" multiple>
          <option v-for="s in allSignalGroups" :key="s" :value="s">{{ s }}</option>
        </select>
        <label>Features:</label>
        <div v-for="f in allFeatures" :key="f">
          <input type="checkbox" v-model="editing.features" :value="f" /> {{ f }}
        </div>
        <label>Laufzeiten & Preise:</label>
        <div v-for="d in editing.durations" :key="d.months">
          {{ d.months }} Monate:
          <input type="number" v-model="d.price" min="1" style="width:60px" /> USDT,
          Rabatt: <input type="number" v-model="d.discount" min="0" max="99" style="width:40px" />%
        </div>
        <button type="submit">Speichern</button>
        <button type="button" @click="editing=null">Abbrechen</button>
      </form>
    </dialog>
  </div>
</template>

<script>
export default {
  name: "PackageManager",
  data() {
    return {
      packages: [],
      editing: null,
      allSignalGroups: ["BTC-Signale", "Altcoin-Signale", "Partner A", "Partner B"],
      allFeatures: [
        "Nachrichten im eigenen Namen weiterleiten",
        "Krypto-News",
        "Coin-Updates",
        "Premium-Support"
      ],
    };
  },
  methods: {
    openDialog() {
      this.editing = {
        name: "",
        groupLimit: 1,
        signalGroups: [],
        features: [],
        durations: [
          { months: 1, price: 0, discount: 0 },
          { months: 3, price: 0, discount: 0 },
          { months: 6, price: 0, discount: 0 },
          { months: 12, price: 0, discount: 0 },
        ]
      };
    },
    edit(pkg) {
      this.editing = JSON.parse(JSON.stringify(pkg));
    },
    del(pkg) {
      this.packages = this.packages.filter(p => p !== pkg);
    },
    save() {
      if (this.editing.id) {
        const i = this.packages.findIndex(p => p.id === this.editing.id);
        this.packages[i] = { ...this.editing };
      } else {
        this.editing.id = Date.now();
        this.packages.push({ ...this.editing });
      }
      this.editing = null;
    }
  }
};
</script>

<!-- Styles werden aus globaler index.css verwendet -->
