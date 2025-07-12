<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import api from './api'

// Hooks auf Top-Level deklarieren
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Automatisches Login für Superuser und registrierte User
onMounted(async () => {
  console.log('🚀 App wird gestartet, prüfe Login-Status...')

  try {
    console.log('🔧 Aktuelle Route:', route.path)
    console.log('🔧 Store Login Status:', authStore.isLoggedIn)

    // Prüfe ob bereits eingeloggt
    if (!authStore.isLoggedIn) {
      console.log('ℹ️ Nicht eingeloggt, versuche Session wiederherzustellen...')

      let sessionRestored = false

      try {
        // Versuche zuerst gespeicherte Session wiederherzustellen
        sessionRestored = await authStore.restoreSession()
        if (sessionRestored) {
          console.log('✅ Session wiederhergestellt')
          // Wenn wir auf der Login-Seite sind, leite zum Dashboard weiter
          if (route.path === '/login') {
            console.log('🔄 Leite zum Dashboard weiter...')
            router.push('/dashboard')
          }
          return
        }
      } catch (error) {
        console.log('ℹ️ Keine gültige Session gefunden:', error.message)
      }

      // Auto-Login: Nutze /auth/auto-login
      const session = localStorage.getItem('wallstreet_session')
      if (session) {
        try {
          const sessionData = JSON.parse(session)
          if (sessionData.telegram_id && sessionData.session_token) {
            console.log('🔄 Versuche Session-basiertes Auto-Login...')
            const response = await api.post('/auth/auto-login', {
              telegram_id: sessionData.telegram_id,
              session_token: sessionData.session_token
            })
            console.log('✅ Automatisches Login erfolgreich:', response.data)
            await authStore.loginSession({
              phone: response.data.user.phone,
              user_id: response.data.user.id,
              telegram_id: response.data.user.telegram_id,
              token: response.data.access_token,
              package_id: response.data.user.package_id,
              is_superadmin: response.data.user.role === 'SUPERADMIN',
              user_name: response.data.user.username
            })
            console.log('✅ Login-Session gespeichert')
            console.log('🔧 Store Login Status nach Login:', authStore.isLoggedIn)
            // Leite zum Dashboard weiter
            console.log('🔄 Leite zum Dashboard weiter...')
            router.push('/dashboard')
            return
          }
        } catch (error) {
          console.log('❌ Session-basiertes Auto-Login fehlgeschlagen:', error.response?.data)
          localStorage.removeItem('wallstreet_session')
        }
      }

      console.log('ℹ️ Kein automatisches Login möglich, zeige Login-Seite')
      // Auch bei Fehler zur Login-Seite weiterleiten, falls nicht bereits dort
      if (route.path !== '/login') {
        router.push('/login')
      }
    } else {
      console.log('✅ Bereits eingeloggt')
      // Wenn wir auf der Login-Seite sind, leite zum Dashboard weiter
      if (route.path === '/login') {
        console.log('🔄 Bereits eingeloggt, leite zum Dashboard weiter...')
        router.push('/dashboard')
      }
    }
  } catch (error) {
    console.error('❌ Fehler beim App-Start:', error)
  }
})
</script>

<style>
#app {
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--bg-primary);
}

@media (max-width: 768px) {
  #app {
    padding: 0;
  }
}
</style>
