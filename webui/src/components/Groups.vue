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

<style scoped>
.groups-page {
  background: #191c22;
  color: #ffb52a;
  min-height: 100vh;
  padding: 28px 18px 18px 18px;
}
.headline {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 18px;
}
.groups-table {
  width: 100%;
  border-spacing: 0;
  margin-bottom: 18px;
  background: #232632;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px #0005;
}
.groups-table th,
.groups-table td {
  padding: 12px 14px;
  border-bottom: 1px solid #232536;
}
.groups-table th {
  background: #21232b;
  color: #ffe199;
  font-size: 1.1rem;
  font-weight: bold;
}
.groups-table td {
  background: #232632;
  color: #ffb52a;
  font-size: 1rem;
}
.status {
  padding: 4px 10px;
  border-radius: 7px;
  font-weight: bold;
}
.status.active {
  background: #19b97c;
  color: #fff;
}
.status.inactive {
  background: #666a80;
  color: #fff;
}
.add-btn, .back-btn, .action-btn {
  margin-top: 10px;
  padding: 8px 16px;
  background: #22263b;
  color: #ffb52a;
  border: none;
  border-radius: 10px;
  font-weight: bold;
  font-size: 1.06rem;
  cursor: pointer;
  margin-right: 10px;
  margin-bottom: 7px;
}
.action-btn.danger {
  background: #ff4b4b;
  color: #fff;
}
.no-groups {
  background: #232632;
  border-radius: 11px;
  padding: 24px;
  color: #ffe199;
  margin-bottom: 22px;
  text-align: center;
  font-size: 1.15rem;
}
</style>
