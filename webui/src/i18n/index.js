// src/i18n/index.js
import { createI18n } from "vue-i18n"
import de from "./de.json"
import en from "./en.json"
import ru from "./ru.json"
import tr from "./tr.json"
import it from "./it.json"

const i18n = createI18n({
  locale: "de",
  fallbackLocale: "en",
  messages: { de, en, ru, tr, it }
})

export default i18n
