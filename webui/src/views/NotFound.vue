<template>
  <div class="min-h-screen bg-gray-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md text-center">
      <h1 class="text-6xl font-bold text-gray-900 mb-4">404</h1>
      <h2 class="text-2xl font-semibold text-gray-700 mb-4">Seite nicht gefunden</h2>
      <p class="text-gray-600 mb-8">
        Die angeforderte Seite existiert nicht oder wurde verschoben.
      </p>
      <router-link 
        to="/dashboard" 
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        Zurück zum Dashboard
      </router-link>
    </div>
  </div>
</template>

<script setup>
// Keine zusätzliche Logik benötigt
</script>
