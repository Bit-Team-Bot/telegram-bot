<template>
  <nav class="sidebar">
    <img src="@/assets/wallstreet-header.png" class="header" />
    <div class="branding">
      <div class="logo-row">
        <img src="@/assets/wallstreet-header.png" class="logo" />
        <span class="brand-text">wallstreet</span>
      </div>
      <span class="subtitle">CRYPTO</span>
    </div>
    <ul>
      <li :class="{active: $route.path === '/dashboard'}" @click="$router.push('/dashboard')">Dashboard</li>
      <li :class="{active: $route.path === '/groups'}" @click="$router.push('/groups')">Groups</li>
      <li :class="{active: $route.path === '/payments'}" @click="$router.push('/payments')">Payments</li>
      <li :class="{active: $route.path === '/settings'}" @click="$router.push('/settings')">Owner Settings</li>
    </ul>
  </nav>
</template>

<!-- Styles werden aus globaler index.css verwendet -->
