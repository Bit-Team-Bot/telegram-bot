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

<style scoped>
.sidebar {
  background: linear-gradient(180deg, #191b23 0%, #232536 80%, #2b3147 100%);
  min-width: 240px;
  max-width: 260px;
  height: 100vh;
  color: #ffb32b;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 4px 0 20px #0008;
  position: fixed;
  top: 0; left: 0;
  z-index: 100;
}
.header {
  width: 100%;
  border-radius: 0 0 24px 24px;
  box-shadow: 0 8px 16px #0004;
  margin-bottom: 10px;
}
.branding {
  text-align: center;
  margin: 16px 0 24px 0;
}
.logo-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.logo {
  height: 32px;
}
.brand-text {
  font-size: 1.7rem;
  font-weight: bold;
  color: #ffb32b;
  letter-spacing: 2px;
}
.subtitle {
  color: #ffe199;
  font-size: 1rem;
  font-weight: 500;
  letter-spacing: 2px;
  margin-top: 4px;
}
ul {
  margin: 32px 0 0 0;
  padding: 0;
  list-style: none;
  width: 100%;
}
li {
  padding: 18px 30px;
  font-size: 1.2rem;
  font-weight: 500;
  color: #ffb32b;
  cursor: pointer;
  border-radius: 12px 0 0 12px;
  margin: 2px 0;
  transition: background 0.14s;
}
li.active, li:hover {
  background: #2b3147;
  color: #ffe199;
  font-weight: 700;
}
@media (max-width: 800px) {
  .sidebar {
    min-width: 80px;
    max-width: 100px;
    font-size: 0.9rem;
    padding: 0 2px;
  }
  .branding, .brand-text, .subtitle {
    display: none;
  }
  ul li {
    padding: 16px 12px;
    font-size: 1rem;
  }
  .header { margin-bottom: 0; }
}
</style>
