# 🤖 Bit-Team-Bot - Automatische Gruppenverwaltung

## 📋 Übersicht

Der Bit-Team-Bot bietet eine vollständige automatische Gruppenverwaltung mit erweiterten Features für Telegram-Gruppen. Beim Hinzufügen des Bots zu einer Gruppe wird automatisch eine Begrüßungsnachricht gesendet, die alle verfügbaren Funktionen erklärt.

## 🚀 Automatische Bot-Begrüßung

### Beim Hinzufügen des Bots zu einer Gruppe:

```
👋 Hallo zusammen! Ich bin der Bit-Team-Bot.

Ich unterstütze euch mit automatischer Gruppenverwaltung und vielen nützlichen Features:

**Gruppenverwaltung – Was ich für Admins kann:**
• User automatisch begrüßen (mit persönlicher Ansprache)
• Willkommensnachrichten frei definierbar (inkl. Platzhalter für Usernamen)
• User muten, verwarnen, kicken (per Knopfdruck oder automatisch)
• Gruppen nachts automatisch schließen/öffnen („Nachtmodus" mit Info-Text)
• Automatische Nachrichten zu bestimmten Zeiten senden (z. B. tägliche Infos)
• Nachrichtenweiterleitung & Screenshots unterbinden
• Regeln & Begrüßungstexte jederzeit anpassbar
• Aktive User-Überwachung (optional)
• Integration mit Webinterface für volle Kontrolle

**Weitere Funktionen:**
– Automatisierte Nachrichten- und Signalweiterleitung (Premium)
– API- und Integrationen (Pro/Expert)
– Statistiken und Reports
– Multi-Language Support

**So geht's los:**
1. Öffne das Webinterface mit dem Button unten oder gebe /start ein.
2. Dort kannst du alle Einstellungen für diese Gruppe verwalten.
3. Hilfe jederzeit mit /help.

Bei Fragen einfach /help in die Gruppe schreiben!
```

## 🛠️ Implementierte Features

### ✅ **Gruppenverwaltung (Alle Pakete)**

#### **User-Management:**
- **Automatische Begrüßung:** Personalisierte Willkommensnachrichten mit Platzhaltern
- **User muten:** Zeitbasierte Mutes (Sekunden bis Stunden)
- **Verwarnungen:** Eskalationssystem mit automatischen Maßnahmen
- **Kick/Remove:** User aus Gruppen entfernen
- **Abschiedsnachrichten:** Automatische Nachrichten beim Verlassen

#### **Gruppen-Steuerung:**
- **Nachtmodus:** Automatisches Schließen/Öffnen zu bestimmten Zeiten
- **Regeln-System:** Anpassbare Gruppenregeln mit Callback-Buttons
- **Begrüßungstexte:** Vollständig editierbare Willkommensnachrichten
- **Platzhalter-System:** `{username}`, `{group_name}`, `{mention}`

#### **Automatisierung:**
- **Zeitgesteuerte Nachrichten:** Automatische Posts zu festen Zeiten
- **Spam-Schutz:** Automatische Löschung von Spam-Nachrichten
- **Nachrichtenweiterleitung:** Verbot von Screenshots und Weiterleitungen
- **User-Überwachung:** Aktivitäts-Tracking (optional)

### 🌐 **Webinterface-Integration**

- **Direkte Verknüpfung:** Webinterface-Button mit User- und Gruppen-ID
- **Admin-Panel:** Vollständige Gruppenverwaltung über Webinterface
- **Einstellungen:** Alle Gruppeneinstellungen online bearbeitbar
- **Statistiken:** Detaillierte Reports und Analytics

### 📱 **Telegram-Integration**

- **Inline-Buttons:** Schnelle Aktionen direkt im Chat
- **Callback-System:** Interaktive Menüs und Aktionen
- **Admin-Rechte-Prüfung:** Automatische Berechtigungsprüfung
- **Multi-Language:** Unterstützung für verschiedene Sprachen

## 🔧 Technische Implementierung

### **Dateien:**
- `bot/group_management.py` - Hauptklasse für Gruppenverwaltung
- `bot/bot.py` - Integration in bestehenden Bot
- `backend/app/routes/admin.py` - Admin-API-Endpoints (korrigiert)

### **Hauptklassen:**

#### **GroupManagement**
```python
class GroupManagement:
    def __init__(self, client: Client)
    async def on_bot_added_to_group(self, message: Message)
    async def on_new_member(self, message: Message)
    async def on_member_left(self, message: Message)
    async def toggle_night_mode(self, chat_id: int, enabled: Optional[bool] = None)
    async def mute_user(self, chat_id: int, user_id: int, duration: int = 300, reason: str = "")
    async def warn_user(self, chat_id: int, user_id: int, reason: str = "")
    async def kick_user(self, chat_id: int, user_id: int, reason: str = "")
    async def send_scheduled_message(self, chat_id: int, message_text: str, schedule_time: str)
```

### **Event-Handler:**
- **Bot hinzugefügt:** Automatische Begrüßung und Admin-Panel
- **Neue Mitglieder:** Personalisierte Willkommensnachrichten
- **Mitglieder verlassen:** Abschiedsnachrichten
- **Callback-Queries:** Interaktive Buttons und Menüs

### **Cache-System:**
- **Gruppeneinstellungen:** Lokaler Cache für bessere Performance
- **Nachtmodus-Status:** Tracking des aktuellen Status
- **Willkommensnachrichten:** Caching für schnelle Zugriffe

## 🎯 Verwendung

### **1. Bot zu Gruppe hinzufügen:**
```
1. Bot als Admin zur Gruppe hinzufügen
2. Automatische Begrüßungsnachricht wird gesendet
3. Webinterface-Button für erweiterte Einstellungen
```

### **2. Gruppeneinstellungen konfigurieren:**
```
1. Webinterface öffnen (Button in Begrüßungsnachricht)
2. Gruppen-ID wird automatisch übertragen
3. Alle Einstellungen online bearbeiten
4. Änderungen werden sofort aktiv
```

### **3. Admin-Funktionen nutzen:**
```
- 🌙 Nachtmodus: Automatisches Schließen/Öffnen
- 👥 User verwalten: Muten, warnen, kicken
- 📋 Regeln: Anpassbare Gruppenregeln
- 🔔 Begrüßungen: Personalisierte Nachrichten
- ⏰ Zeitplanung: Automatische Nachrichten
```

## 🔒 Sicherheit & Berechtigungen

### **Admin-Rechte:**
- Automatische Prüfung der Admin-Berechtigungen
- Nur Admins können Verwaltungsfunktionen nutzen
- Bot benötigt Admin-Rechte für alle Funktionen

### **Datenschutz:**
- Lokaler Cache für Gruppeneinstellungen
- Keine dauerhafte Speicherung sensibler Daten
- Sichere API-Kommunikation

## 📊 Features nach Paket-Level

### **Basic:**
- ✅ Automatische Begrüßung
- ✅ User muten/warnen/kicken
- ✅ Nachtmodus
- ✅ Anpassbare Regeln
- ✅ Webinterface-Integration

### **Pro:**
- ✅ Alle Basic-Features
- ✅ Erweiterte Statistiken
- ✅ Multi-Gruppen-Management
- ✅ Geplante Nachrichten
- ✅ User-Überwachung

### **Expert:**
- ✅ Alle Pro-Features
- ✅ API-Integrationen
- ✅ Erweiterte Automatisierung
- ✅ Custom Scripts
- ✅ Multi-Language Support

## 🚀 Installation & Setup

### **1. Abhängigkeiten installieren:**
```bash
pip install pyrogram telethon
```

### **2. Konfiguration:**
```python
# config.py
API_ID = "your_api_id"
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"
WEBUI_URL = "https://webui.bit-team-bot.online"
BACKEND_URL = "https://api.bit-team-bot.online"
```

### **3. Bot starten:**
```bash
cd bot
python bot.py
```

## 🔧 Konfiguration

### **Standard-Einstellungen:**
```python
group_settings = {
    "welcome_enabled": True,
    "welcome_message": "Standard-Begrüßung...",
    "goodbye_enabled": False,
    "show_welcome_buttons": True,
    "night_mode_enabled": False,
    "night_mode_start": "22:00",
    "night_mode_end": "08:00",
    "auto_delete_spam": True,
    "max_warnings": 3,
    "rules_text": "Standard-Regeln..."
}
```

### **Platzhalter-System:**
- `{username}` - Name des Users
- `{group_name}` - Name der Gruppe
- `{mention}` - Telegram-Mention-Link

## 📝 Logging

### **Log-Level:**
- **INFO:** Normale Operationen
- **WARNING:** Nicht-kritische Fehler
- **ERROR:** Kritische Fehler

### **Log-Datei:**
```
bot.log - Alle Bot-Aktivitäten
```

## 🐛 Troubleshooting

### **Häufige Probleme:**

1. **Bot hat keine Admin-Rechte:**
   - Bot als Admin zur Gruppe hinzufügen
   - Alle notwendigen Berechtigungen erteilen

2. **Begrüßungsnachricht wird nicht gesendet:**
   - Prüfe Logs auf Fehler
   - Stelle sicher, dass Bot Admin ist

3. **Nachtmodus funktioniert nicht:**
   - Prüfe Zeitformat (HH:MM)
   - Stelle sicher, dass Bot Berechtigung hat

## 🔄 Updates & Wartung

### **Regelmäßige Updates:**
- Pyrogram-Bibliothek aktualisieren
- Sicherheits-Patches einspielen
- Neue Features hinzufügen

### **Backup:**
- Gruppeneinstellungen regelmäßig sichern
- Log-Dateien rotieren
- Konfiguration dokumentieren

## 📞 Support

Bei Fragen oder Problemen:
- **Telegram:** @bit_team_support
- **Email:** support@bit-team-bot.online
- **Dokumentation:** https://docs.bit-team-bot.online

---

**🎉 Die automatische Gruppenverwaltung ist vollständig implementiert und einsatzbereit!** 