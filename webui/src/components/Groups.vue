<template>
  <div class="groups-page">
    <h2 class="headline">Gruppenverwaltung</h2>

    <div v-if="groups.length === 0" class="no-groups">
      Du hast aktuell keine Gruppen angelegt.
    </div>
    <div v-else>
      <table class="groups-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Typ</th>
            <th>Mitglieder</th>
            <th>Status</th>
            <th>Aktionen</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="g in groups" :key="g.id">
            <td>{{ g.name }}</td>
            <td>{{ g.type }}</td>
            <td>{{ g.members }}</td>
            <td>
              <span :class="['status', g.active ? 'active' : 'inactive']">
                {{ g.active ? 'aktiv' : 'inaktiv' }}
              </span>
            </td>
            <td>
              <button class="action-btn" @click="editGroup(g)">Bearbeiten</button>
              <button class="action-btn danger" @click="deleteGroup(g.id)">Löschen</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <button class="add-btn" @click="addGroup">+ Neue Gruppe anlegen</button>
    <button class="back-btn" @click="$router.back()">Zurück</button>
  </div>
</template>

<script setup>
import { ref } from "vue";

// Demo-Daten, später API anbinden
const groups = ref([
  {
    id: 1,
    name: "Krypto News Channel",
    type: "Supergruppe",
    members: 152,
    active: true
  },
  {
    id: 2,
    name: "Altcoin Talk",
    type: "Normale Gruppe",
    members: 48,
    active: false
  }
]);

function addGroup() {
  alert("Gruppe anlegen – kommt als Dialog oder auf neuer Seite.");
}
function editGroup(g) {
  alert("Bearbeiten (kommt später als Dialog).");
}
function deleteGroup(id) {
  if (confirm("Gruppe wirklich löschen?")) {
    const idx = groups.value.findIndex(g => g.id === id);
    if (idx !== -1) groups.value.splice(idx, 1);
  }
}
</script>

<!-- Styles werden aus globaler index.css verwendet -->
