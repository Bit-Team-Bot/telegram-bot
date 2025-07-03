<template>
  <div class="feature-manager">
    <h1>Zusatzfeatures Verwaltung</h1>
    <button @click="openDialog()">+ Feature hinzufügen</button>
    <table>
      <tr>
        <th>Name</th><th>Preis/Monat</th><th>Rabatte</th><th>Aktion</th>
      </tr>
      <tr v-for="f in features" :key="f.id">
        <td>{{ f.name }}</td>
        <td>{{ f.basePrice }} USDT</td>
        <td>
          <span v-for="d in f.discounts" :key="d.months">
            {{ d.months }}M: {{ d.discount }}%
          </span>
        </td>
        <td>
          <button @click="edit(f)">Edit</button>
          <button @click="del(f)">Löschen</button>
        </td>
      </tr>
    </table>
    <dialog v-if="editing">
      <form @submit.prevent="save">
        <input v-model="editing.name" placeholder="Feature-Name" required/>
        <label>Basispreis (USDT/Monat):</label>
        <input type="number" v-model="editing.basePrice" min="0" required />
        <label>Rabatte (je Dauer):</label>
        <div v-for="d in editing.discounts" :key="d.months">
          {{ d.months }} Monate:
          <input type="number" v-model="d.discount" min="0" max="99" /> %
        </div>
        <button type="submit">Speichern</button>
        <button type="button" @click="editing=null">Abbrechen</button>
      </form>
    </dialog>
  </div>
</template>

<script>
export default {
  name: "FeatureManager",
  data() {
    return {
      features: [],
      editing: null,
    };
  },
  created() {
    // Demo-Daten – später per API
    this.features = [
      {
        id: 1,
        name: "Nachrichten im eigenen Namen weiterleiten",
        basePrice: 9,
        discounts: [
          { months: 3, discount: 10 },
          { months: 6, discount: 20 },
          { months: 12, discount: 30 }
        ]
      }
    ];
  },
  methods: {
    openDialog() {
      this.editing = {
        name: "",
        basePrice: 0,
        discounts: [
          { months: 3, discount: 0 },
          { months: 6, discount: 0 },
          { months: 12, discount: 0 }
        ]
      };
    },
    edit(f) {
      this.editing = JSON.parse(JSON.stringify(f));
    },
    del(f) {
      this.features = this.features.filter(x => x !== f);
    },
    save() {
      if (this.editing.id) {
        const i = this.features.findIndex(x => x.id === this.editing.id);
        this.features[i] = { ...this.editing };
      } else {
        this.editing.id = Date.now();
        this.features.push({ ...this.editing });
      }
      this.editing = null;
    }
  }
};
</script>

<style scoped>
.feature-manager {
  padding: 40px;
  color: #ffb52a;
  background: #191c22;
}
table {
  width: 100%;
  margin-top: 24px;
  background: #232632;
  color: #fff;
  border-radius: 8px;
  overflow: hidden;
}
th, td {
  padding: 10px;
  text-align: left;
}
dialog {
  position: fixed;
  top: 15vh;
  left: 50vw;
  transform: translate(-50%,0);
  background: #232632;
  color: #fff;
  padding: 30px;
  border-radius: 14px;
  box-shadow: 0 2px 24px #0007;
}
form > * { display: block; margin-bottom: 14px; }
input[type="number"], input[type="text"] { background: #2c2f3a; color: #ffe199; border: none; border-radius: 6px; padding: 6px 8px; }
button { background: #ffb52a; color: #232632; border: none; border-radius: 8px; font-weight: bold; margin-right: 12px; padding: 8px 16px; }
button[type="button"] { background: #888; color: #fff; }
</style>
