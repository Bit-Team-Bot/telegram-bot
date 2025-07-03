<template>
  <nav class="sidebar">
    <img src="@/assets/wallstreet-header.png" class="logo" alt="Wallstreet Crypto" />
    <ul>
      <li :class="{active: isActive('/dashboard')}" @click="go('/dashboard')">
        <img src="@/assets/home.png" class="nav-icon" /> Dashboard
      </li>
      <li :class="{active: isActive('/groups')}" @click="go('/groups')">
        <img src="@/assets/groups.png" class="nav-icon" /> Gruppen
      </li>
      <li :class="{active: isActive('/payments')}" @click="go('/payments')">
        <img src="@/assets/payments.png" class="nav-icon" /> Zahlungen
      </li>
      <li :class="{active: isActive('/owner-settings')}" @click="go('/owner-settings')">
        <img src="@/assets/settings.png" class="nav-icon" /> Owner Settings
      </li>
      <li class="mt-auto" @click="logout">
        <img src="@/assets/logout.png" class="nav-icon" /> Logout
      </li>
    </ul>
  </nav>
</template>

<script setup>
import { useRouter, useRoute } from "vue-router"

const router = useRouter()
const route = useRoute()

function go(path) {
  if (route.path !== path) router.push(path)
}

function isActive(path) {
  return route.path === path
}

function logout() {
  // Logout-Logik
  router.push("/")
}
</script>

<style scoped>
.sidebar {
  background: #191c22;
  color: #ffb52a;
  width: 90px;
  min-width: 90px;
  height: 100vh;
  padding: 18px 8px 12px 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: fixed;
  left: 0;
  top: 0;
  box-shadow: 2px 0 14px #0007;
  z-index: 50;
}
.logo {
  width: 50px;
  margin-bottom: 22px;
  border-radius: 50%;
  box-shadow: 0 0 7px #ffb52a77;
}
ul {
  width: 100%;
  padding: 0;
  margin: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
li {
  width: 100%;
  padding: 8px 2px 8px 2px;
  margin-bottom: 2px;
  text-align: left;
  border-radius: 10px;
  font-size: 1.01rem;
  font-weight: 500;
  cursor: pointer;
  color: #ffb52a;
  display: flex;
  align-items: center;
  transition: background 0.15s;
}
li.active, li:hover {
  background: #22263b;
  color: #fff;
}
li.mt-auto {
  margin-top: auto;
  background: #2a2530;
  color: #ff6767;
}
.nav-icon {
  width: 26px;
  height: 26px;
  margin-right: 7px;
  filter: brightness(1.3);
}
@media (max-width: 800px) {
  .sidebar {
    width: 64px;
    min-width: 64px;
    padding-left: 3px;
    padding-right: 3px;
  }
  .logo { width: 38px; }
  .nav-icon { width: 20px; height: 20px; }
  li { font-size: 0.87rem; }
}
</style>
