<template>
  <div class="support-container" style="background:var(--bt-bg-dark);min-height:100vh;padding:32px 0;">
    <main class="support-content" style="max-width:900px;margin:0 auto;">
      <div class="page-header" style="text-align:center;margin-bottom:32px;">
        <h1 class="section-title">Support</h1>
        <p style="color:var(--bt-text-muted);">Hilfe und Kontakt</p>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;">
        <BaseCard style="flex-direction:column;align-items:flex-start;">
          <h2 style="color:var(--bt-orange);margin-bottom:10px;">Häufige Fragen</h2>
          <div v-for="(faq, index) in faqs" :key="index" style="margin-bottom:14px;">
            <div @click="toggleFaq(index)" style="cursor:pointer;display:flex;align-items:center;">
              <span class="material-icons" style="margin-right:8px;">help_outline</span>
              <h3 style="margin:0;font-size:1.1rem;">{{ faq.question }}</h3>
              <span class="material-icons" style="margin-left:auto;">{{ faq.open ? 'expand_less' : 'expand_more' }}</span>
            </div>
            <div v-show="faq.open" style="margin-left:32px;margin-top:4px;color:var(--bt-text-muted);">
              <p>{{ faq.answer }}</p>
            </div>
          </div>
        </BaseCard>
        <BaseCard style="flex-direction:column;align-items:flex-start;">
          <h2 style="color:var(--bt-orange);margin-bottom:10px;">Kontaktieren Sie uns</h2>
          <div class="form-group" style="margin-bottom:10px;width:100%;">
            <label style="color:var(--bt-orange);">Betreff</label>
            <select v-model="contactForm.subject" style="width:100%;padding:8px 12px;border-radius:8px;background:#232632;color:var(--bt-text-white);">
              <option value="">Bitte wählen Sie einen Betreff</option>
              <option value="technical">Technisches Problem</option>
              <option value="billing">Abrechnung</option>
              <option value="account">Konto-Probleme</option>
              <option value="general">Allgemeine Fragen</option>
            </select>
          </div>
          <div class="form-group" style="margin-bottom:10px;width:100%;">
            <label style="color:var(--bt-orange);">Nachricht</label>
            <textarea v-model="contactForm.message" style="width:100%;padding:10px 14px;border-radius:8px;background:#232632;color:var(--bt-text-white);" rows="6" placeholder="Beschreiben Sie Ihr Problem oder Ihre Frage..."></textarea>
          </div>
          <BaseButton @click="submitContact" :disabled="submitting" style="width:100%;">
            <span class="material-icons" style="vertical-align:middle;margin-right:4px;">send</span>
            {{ submitting ? 'Wird gesendet...' : 'Nachricht senden' }}
          </BaseButton>
        </BaseCard>
      </div>
      <div style="margin-top:32px;display:grid;grid-template-columns:repeat(3,1fr);gap:18px;">
        <BaseCard v-for="(info, idx) in contactInfos" :key="idx" style="flex-direction:column;align-items:center;text-align:center;">
          <span class="material-icons" style="font-size:32px;margin-bottom:8px;">{{ info.icon }}</span>
          <h3 style="color:var(--bt-orange);margin-bottom:4px;">{{ info.title }}</h3>
          <p style="color:var(--bt-text-white);margin-bottom:2px;">{{ info.value }}</p>
          <p style="color:var(--bt-text-muted);font-size:0.98em;">{{ info.note }}</p>
        </BaseCard>
      </div>
      <div style="margin-top:32px;text-align:center;">
        <BaseButton style="background:#888;color:#fff;" @click="$router.push('/dashboard')">
  <span class="material-icons" style="vertical-align:middle;margin-right:4px;">arrow_back</span>Zurück zum Dashboard
</BaseButton>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import BaseCard from '../components/BaseCard.vue'
import BaseButton from '../components/BaseButton.vue'

const router = useRouter()
const submitting = ref(false)
const contactForm = ref({ subject: '', message: '' })
const faqs = ref([
  { question: 'Wie kann ich mein Paket upgraden?', answer: 'Sie können Ihr Paket über die Pakete-Seite upgraden. Wählen Sie das gewünschte Paket aus und folgen Sie den Anweisungen zur Zahlung.', open: false },
  { question: 'Wie funktioniert die Zahlung?', answer: 'Wir akzeptieren verschiedene Kryptowährungen. Nach der Zahlung wird Ihr Konto automatisch freigeschaltet.', open: false },
  { question: 'Kann ich mein Konto löschen?', answer: 'Ja, Sie können Ihr Konto in den Einstellungen löschen. Beachten Sie, dass diese Aktion nicht rückgängig gemacht werden kann.', open: false },
  { question: 'Wie lange dauert die Aktivierung?', answer: 'Nach erfolgreicher Zahlung wird Ihr Konto innerhalb von 10-30 Minuten aktiviert.', open: false },
  { question: 'Was passiert bei technischen Problemen?', answer: 'Bei technischen Problemen kontaktieren Sie uns bitte über den Support. Wir werden das Problem schnellstmöglich beheben.', open: false }
])
const contactInfos = [
  { icon: 'email', title: 'E-Mail', value: 'support@bit-team-bot.online', note: 'Antwort innerhalb von 24 Stunden' },
  { icon: 'chat', title: 'Telegram', value: '@bit_team_support', note: 'Sofortige Antwort möglich' },
  { icon: 'smartphone', title: 'WhatsApp', value: '+49 123 456789', note: 'Mo-Fr 9:00-18:00 Uhr' }
]
const toggleFaq = (index) => { faqs.value[index].open = !faqs.value[index].open }
const submitContact = async () => {
  if (!contactForm.value.subject || !contactForm.value.message) { alert('Bitte füllen Sie alle Felder aus.'); return }
  submitting.value = true
  try {
    await api.post('/support/contact', contactForm.value)
    alert('Ihre Nachricht wurde erfolgreich gesendet. Wir werden uns schnellstmöglich bei Ihnen melden.')
    contactForm.value = { subject: '', message: '' }
  } catch (err) {
    alert('Fehler beim Senden der Nachricht. Bitte versuchen Sie es erneut.')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
/* Alle alten Styles entfernt, alles läuft über globale Styles */
</style> 