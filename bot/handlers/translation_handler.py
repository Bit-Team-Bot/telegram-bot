# handlers/translation_handler.py

class TranslationHandler:
    def __init__(self, mode="static"):
        self.mode = mode

    async def translate(self, text, lang="de"):
        # Platz für echte KI-Übersetzung (OpenAI/DeepL) oder feste Dictionarys
        translations = {
            "de": text,
            "en": text,  # Default: einfach zurückgeben
            "ru": text,
            "tr": text,
            "it": text
        }
        return translations.get(lang, text)
