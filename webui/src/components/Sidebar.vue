<template>
  <nav class="sidebar">
    <img src="@/assets/wallstreet-header.png" class="logo" alt="Wallstreet Crypto" />
    <ul>
      <li :class="{active: isActive('/packages')}" @click="go('/packages')">
        <img src="@/assets/packages.png" class="nav-icon" /> Pakete
      </li>
      <li :class="{active: isActive('/groups')}" @click="go('/groups')">
        <img src="@/assets/groups.png" class="nav-icon" /> Gruppen
      </li>
      <li :class="{active: isActive('/payments')}" @click="go('/payments')">
        <img src="@/assets/payments.png" class="nav-icon" /> Zahlungen
      </li>
      <li :class="{active: isActive('/signal-groups')}" @click="go('/signal-groups')">
        <img src="@/assets/signal-groups.png" class="nav-icon" /> Signalgruppen
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
</script>

<!-- Styles werden aus globaler index.css verwendet -->
