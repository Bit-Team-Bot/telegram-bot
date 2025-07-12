import { createApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia'
import router from './router'
import { createI18n } from 'vue-i18n'
import de from './i18n/de.json'
import en from './i18n/en.json'
import './index.css'
import { useAuthStore } from '../src/stores/auth'

// Router-Guard für Authentifizierung und Telegram-ID-Login
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  // Erlaube Login-Seite immer, wenn ein Telegram-ID-Parameter in der URL ist
  if (to.path === '/login' && (to.query.telegram_id || to.query.user || to.query.tgid)) {
    return next()
  }
  // Standard-Auth-Check
  if (!authStore.isAuthenticated && to.path !== '/login') {
    // Query-Parameter beim Redirect erhalten!
    return next({ path: '/login', query: to.query })
  }
  next()
})

const i18n = createI18n({
  legacy: false,
  locale: 'de',
  fallbackLocale: 'en',
  messages: { de, en }
})

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(i18n)
app.mount('#app')
