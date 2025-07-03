<template>
  <button class="nav-button" @click="$router.push(route)">
    <svg class="nav-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <component :is="iconComponent" />
    </svg>
    <span class="nav-text">{{ text }}</span>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  text: {
    type: String,
    required: true
  },
  route: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    required: true
  }
})

const iconComponent = computed(() => {
  const icons = {
    dashboard: {
      template: `
        <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z" fill="currentColor"/>
      `
    },
    packages: {
      template: `
        <path d="M21 16.5C21 16.88 20.79 17.21 20.47 17.38L12.57 21.82C12.41 21.94 12.21 22 12 22C11.79 22 11.59 21.94 11.43 21.82L3.53 17.38C3.21 17.21 3 16.88 3 16.5V7.5C3 7.12 3.21 6.79 3.53 6.62L11.43 2.18C11.59 2.06 11.79 2 12 2C12.21 2 12.41 2.06 12.57 2.18L20.47 6.62C20.79 6.79 21 7.12 21 7.5V16.5M12 4.15L6.04 7.5L12 10.85L17.96 7.5L12 4.15M5 15.91L11 19.29V12.58L5 9.21V15.91M19 15.91V9.21L13 12.58V19.29L19 15.91Z" fill="currentColor"/>
      `
    },
    groups: {
      template: `
        <path d="M16 4C16 2.89 15.11 2 14 2C12.89 2 12 2.89 12 4C12 5.11 12.89 6 14 6C15.11 6 16 5.11 16 4M20 22V16H16.5L15.56 15H8.44L7.5 16H4V22H20M22 22H2V16C2 14.89 2.89 14 4 14H7L8 12H16L17 14H20C21.11 14 22 14.89 22 16V22M10 4C10 2.89 9.11 2 8 2C6.89 2 6 2.89 6 4C6 5.11 6.89 6 8 6C9.11 6 10 5.11 10 4Z" fill="currentColor"/>
      `
    },
    payments: {
      template: `
        <path d="M20 4H4C2.89 4 2 4.89 2 6V18C2 19.11 2.89 20 4 20H20C21.11 20 22 19.11 22 18V6C22 4.89 21.11 4 20 4M20 18H4V12H20V18M20 8H4V6H20V8M14 16H6V14H14V16Z" fill="currentColor"/>
      `
    }
  }
  
  return icons[props.icon] || icons.dashboard
})
</script>

<style scoped>
.nav-icon {
  width: 32px;
  height: 32px;
  fill: var(--text-white);
}

.nav-text {
  font-weight: bold;
  font-size: 1.1rem;
}
</style> 