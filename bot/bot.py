import logging
from pyrogram.client import Client
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, MenuButtonWebApp
import requests
import asyncio
from bot.config import API_ID, API_HASH, BOT_TOKEN, WEBUI_URL, BACKEND_URL, USERBOT_SERVICE_URL
from datetime import datetime
from bot.handlers.group_management import GroupManagement
import sys
from bot.api_client import APIClient
import aiohttp
import xml.etree.ElementTree as ET
from pyrogram.enums import ChatType, ChatMembersFilter
from bot.handlers.group_admin_menu_handlers import GroupAdminMenu, register_group_admin_menu_handlers
from bot.bot_utils import fetch_crypto_news, fetch_joke
from bot.handlers.trigger_handler import TriggerHandler

print("[DEBUG] bot.py gestartet")

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 10

# Sicherstellen, dass die Konfigurationswerte nicht None sind
if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError("API_ID, API_HASH und BOT_TOKEN müssen in der config.py definiert sein")

app = Client("bitteam-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Gruppenverwaltung initialisieren
group_management = GroupManagement(app)
group_admin_menu = GroupAdminMenu(
    app,
    get_group_settings=group_management.get_group_settings,
    get_default_welcome_message=group_management.get_default_welcome_message
)

print("Bot startet, Handler werden registriert...")

# --- Gruppenverwaltungs-Handler direkt beim Start initialisieren ---
async def init_group_management():
    pass

async def notify_admins_after_restart():
    """Benachrichtigt alle bekannten Gruppen-Admins mit bestehendem Privat-Chat nach Neustart."""
    try:
        # Alle Dialoge (Privat-Chats) holen
        private_user_ids = set()
        dialogs = []
        dialogs_gen = await app.get_dialogs()
        if dialogs_gen is not None:
            async for d in dialogs_gen:
                dialogs.append(d)
        for d in dialogs:
            if d.chat.type == ChatType.PRIVATE:
                private_user_ids.add(d.chat.id)

        # Alle Gruppen, in denen der Bot Mitglied ist, holen
        groups = []
        for d in dialogs:
            if d.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
                groups.append(d)
        notified = set()
        for group in groups:
            chat_id = group.chat.id
            # Alle Admins der Gruppe holen
            try:
                members_gen = await app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS)
                if members_gen is not None:
                    async for member in members_gen:
                        user = member.user
                        if user.is_bot:
                            continue
                        if user.id in private_user_ids and user.id not in notified:
                            try:
                                await app.send_message(
                                    user.id,
                                    f"✅ Der Bot ist nach einem Neustart wieder online und einsatzbereit für die Gruppe: {group.chat.title} (ID: {chat_id})"
                                )
                                notified.add(user.id)
                            except Exception as e:
                                logger.warning(f"Konnte Admin {user.id} nicht benachrichtigen: {e}")
            except Exception as e:
                logger.warning(f"Fehler beim Ermitteln der Admins für Gruppe {chat_id}: {e}")
        logger.info(f"Benachrichtigung nach Neustart an {len(notified)} Admins gesendet.")
    except Exception as e:
        logger.error(f"Fehler bei Admin-Benachrichtigung nach Neustart: {e}")

# Initialisierung beim Start (vor app.run())
import asyncio
asyncio.get_event_loop().run_until_complete(notify_admins_after_restart())

print("Python:", sys.version)
try:
    print("Pyrogram:", __import__('pyrogram').__version__)
except Exception as e:
    print("Pyrogram nicht geladen:", e)
try:
    print("tgcrypto:", __import__('tgcrypto').__version__)
except Exception as e:
    print("tgcrypto nicht geladen:", e)
try:
    print("Telethon:", __import__('telethon').__version__)
except Exception as e:
    print("Telethon nicht geladen:", e)

backend_client = APIClient(BACKEND_URL)
userbot_client = APIClient(USERBOT_SERVICE_URL)

class BotError(Exception):
    """Custom exception für Bot-Fehler"""
    pass

async def get_user_status(telegram_id):
    """Holt User-Status vom Backend - EINZIGE Datenquelle"""
    try:
        data = backend_client.get(f"/users/{telegram_id}/is_paid")
        return {
            "is_paid": data.get("is_paid", False),
            "active_package": data.get("active_package"),
            "user_id": data.get("user_id")
        }
    except Exception:
        return {"is_paid": False, "active_package": None, "user_id": None}

def create_main_menu(user_id, user_status, use_webapp=True):
    """Erstellt dynamisches Hauptmenü basierend auf User-Status"""
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
    from bot.config import WEBUI_URL
        btns = [
        [InlineKeyboardButton("🌐 Webinterface öffnen", web_app=WebAppInfo(url=f"{WEBUI_URL}?user={user_id}"))]
    ]
    return InlineKeyboardMarkup(btns)

# Gruppenverwaltung initialisieren (beim ersten Aufruf)
_group_management_initialized = False

# /menu nur in Gruppen, /start nur im privaten Chat
@app.on_message(filters.command("menu") & filters.group)
async def menu_command_handler(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    try:
        member = await client.get_chat_member(chat_id, user_id)
        admin_status_values = ["creator", "administrator", "owner"]
        status_str = str(member.status).lower()
        is_admin = any(s in status_str for s in admin_status_values)
    except Exception:
        is_admin = False
    keyboard = group_admin_menu.get_group_main_menu(chat_id, is_admin=is_admin)
    await message.reply("Gruppenmenü:", reply_markup=keyboard)

# /start nur für private Chats
@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    logger.info(f"🚀 /start von User {user_id} ({user_name})")
    try:
        user_data = {
            "telegram_id": str(user_id),
            "user_name": user_name,
            "first_name": user_name,
            "last_name": message.from_user.last_name,
            "username": message.from_user.username,
            "is_bot": message.from_user.is_bot,
            "language_code": message.from_user.language_code
        }
        response = backend_client.post("/users/register_or_update", user_data)
        logger.info(f"✅ User-Daten an Backend gesendet für {user_id}: {response}")
    except BotError as e:
        logger.warning(f"❌ Konnte User-Daten nicht an Backend senden: {e}")
    except Exception as e:
        logger.error(f"❌ Fehler beim Senden der User-Daten: {e}")
    webapp_url = f"{WEBUI_URL}?user={user_id}"
    keyboard = create_main_menu(str(user_id), {"is_paid": False}, use_webapp=True)
    response_text = (
        "Willkommen!\n\n"
        "🌐 Klicke auf den Button unten, um das Webinterface als Mini-App zu öffnen.\n\n"
        "ℹ️ <b>Wichtig:</b> <b>/start</b> funktioniert nur im <b>privaten Chat</b> mit dem Bot.\n"
        "In Gruppen kannst du als Admin das Menü mit <b>/menu</b> aufrufen.\n"
        "\n🆔 <b>Deine Telegram-ID:</b> <code>{user_id}</code>"
    )
    await message.reply(response_text, reply_markup=keyboard)
    logger.info(f"✅ Antwort an User {user_id} gesendet")

@app.on_message(filters.contact)
async def contact_handler(client, message):
    phone = message.contact.phone_number
    telegram_id = message.from_user.id
    user_name = message.from_user.first_name
    logger.info(f"Kontakt von User {telegram_id} ({user_name}): {phone}")
    try:
        payload = {
            "telegram_id": str(telegram_id),
            "phone": phone
        }
        # Verwende die neue Bot-Route ohne Authentifizierung
        response = await userbot_client.post("/users/link_phone_bot", payload)
        logger.info(f"✅ Telefonnummer verknüpft: {response}")
        if message.chat.type in ["group", "supergroup"]:
            try:
                member = await app.get_chat_member(message.chat.id, message.from_user.id)
                is_admin = member.status in ["creator", "administrator"]
            except Exception:
                is_admin = False
            reply_markup = group_admin_menu.get_group_main_menu(str(telegram_id), is_admin=is_admin)
        else:
            reply_markup = create_main_menu(str(telegram_id), {"is_paid": False}, use_webapp=False)
        await message.reply(
            "✅ Deine Telefonnummer wurde erfolgreich verknüpft!\n\n"
            "Du kannst dich jetzt im Webinterface anmelden.",
            reply_markup=reply_markup
        )
    except BotError as e:
        logger.error(f"Fehler bei Kontakt-Registrierung: {e}")
        await message.reply(f"❌ Fehler bei der Registrierung: {str(e)}")
    except Exception as e:
        logger.error(f"Unerwarteter Fehler bei Kontakt-Registrierung: {e}")
        await message.reply("❌ Es gab einen unerwarteten Fehler. Kontaktiere den Support.")

@app.on_callback_query(filters.regex(r"^(news|package_status|payments|buy_package|logout)$"))
async def handle_callback(client, callback_query):
    user_id = str(callback_query.from_user.id)
    user_name = callback_query.from_user.first_name
    callback_data = callback_query.data
    logger.info(f"Callback von User {user_id} ({user_name}): {callback_data}")
    try:
        user_status = await get_user_status(user_id)
        chat = callback_query.message.chat
        is_group = chat.type in ["group", "supergroup"]
        is_admin = False
        if is_group:
            try:
                member = await app.get_chat_member(chat.id, callback_query.from_user.id)
                is_admin = member.status in ["creator", "administrator"]
            except Exception:
                is_admin = False
        if callback_data == "news":
            news_text = await fetch_crypto_news()
            await callback_query.message.edit_text(
                news_text,
                reply_markup=group_admin_menu.get_group_main_menu(user_id, is_admin=is_admin),
                disable_web_page_preview=True
            )

        elif callback_data == "package_status":
            package_name = user_status.get("active_package", "Kein Paket")
            is_paid = user_status.get("is_paid", False)
            status_text = f"🧾 **Paketstatus**\n\n"
            status_text += f"**Paket:** {package_name}\n"
            status_text += f"**Status:** {'✅ Aktiv' if is_paid else '❌ Inaktiv'}\n"
            if is_paid:
                status_text += "\nDu hast Zugang zu allen Premium-Features!"
            else:
                status_text += "\nKaufe ein Paket für Premium-Features."
            await callback_query.message.edit_text(
                status_text,
                reply_markup=group_admin_menu.get_group_main_menu(user_id, is_admin=is_admin)
            )
        elif callback_data == "payments":
            if user_status.get("is_paid"):
                try:
                    payments_data = backend_client.get(f"/payments/user/{user_id}")
                    payments_text = "💰 **Deine Zahlungen**\n\n"
                    if payments_data:
                        for payment in payments_data[:5]:
                            amount = payment.get("amount", 0)
                            date = payment.get("created_at", "Unbekannt")
                            payments_text += f"💵 {amount}€ - {date}\n"
                    else:
                        payments_text += "Keine Zahlungen gefunden."
                    await callback_query.message.edit_text(
                        payments_text,
                        reply_markup=group_admin_menu.get_group_main_menu(user_id, is_admin=is_admin)
                    )
                except BotError:
                    await callback_query.message.edit_text(
                        "❌ Fehler beim Laden der Zahlungen.",
                        reply_markup=group_admin_menu.get_group_main_menu(user_id, is_admin=is_admin)
                    )
            else:
                await callback_query.message.edit_text(
                    "🔒 **Nur für zahlende Nutzer**\n\n"
                    "Du benötigst ein aktives Paket, um deine Zahlungen zu sehen.",
                    reply_markup=group_admin_menu.get_group_main_menu(user_id, is_admin=is_admin)
                )
        elif callback_data == "buy_package":
            await callback_query.message.edit_text(
                "💸 **Paket kaufen**\n\n"
                "Besuche das Webinterface, um ein Paket zu kaufen:\n"
                "🌐 https://webui.bit-team-bot.online\n\n"
                "Oder kontaktiere den Support für weitere Informationen.",
                reply_markup=group_admin_menu.get_group_main_menu(user_id, is_admin=is_admin)
            )
        elif callback_data == "logout":
            await callback_query.message.edit_text(
                "🚪 **Auf Wiedersehen!**\n\n"
                "Du wurdest erfolgreich ausgeloggt.\n"
                "Bis bald! 😘"
            )

    except Exception as e:
        logger.error(f"Fehler im Callback-Handler: {e}")
        await callback_query.message.edit_text(
            "❌ Es gab einen Fehler. Versuche es später erneut.",
            reply_markup=group_admin_menu.get_group_main_menu(user_id, is_admin=False)
        )

@app.on_message(filters.command("help"))
async def help_handler(client, message):
    help_text = (
        "ℹ️ <b>Telegram Bot Hilfe</b>\n\n"
        "<b>Verfügbare Befehle:</b>\n"
        "/start – Hauptmenü öffnen (nur im <b>privaten Chat</b>)\n"
        "/help – Diese Hilfe anzeigen\n"
        "/menu – Admin-Menü (nur in Gruppen für Admins)\n\n"
        "<b>Hinweise:</b>\n"
        "• <b>/start</b> funktioniert ausschließlich im privaten Chat mit dem Bot.\n"
        "• In Gruppen können Admins das Menü mit <b>/menu</b> aufrufen.\n\n"
        "<b>Weitere Funktionen:</b>\n"
        "• Automatische Begrüßung neuer Mitglieder\n"
        "• Gruppenverwaltung, Mute, Kick, Warnungen\n"
        "• Webinterface für Einstellungen\n"
        "• Triggerworte für spezielle Aktionen (z.B. 'news', 'witz')\n\n"
        "Bei Fragen einfach /help in die Gruppe schreiben!"
    )
    await message.reply(help_text)

ADMIN_CHAT_ID = None
try:
    from config import ADMIN_CHAT_ID
except ImportError:
    pass

def send_admin_alert(message):
    if not ADMIN_CHAT_ID or not BOT_TOKEN:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": ADMIN_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        logger.error(f"Fehler beim Senden der Admin-Benachrichtigung: {e}")

def handle_exception(exc_type, exc_value, exc_traceback):
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    send_admin_alert(f"[BOT-ALERT] Uncaught exception: {exc_value}")
sys.excepthook = handle_exception

@app.on_callback_query(filters.regex(r"^admin_welcome_[0-9]+$"))
async def test_admin_welcome_handler(client, callback_query):
    print(">>> DIREKT IM HAUPTMODUL: admin_welcome_handler wurde aufgerufen!", callback_query.data)
    await callback_query.answer("Direkter Handler!", show_alert=True)

@app.on_callback_query(filters.regex(r"^group_admin_[0-9]+$"))
async def test_group_admin_handler(client, callback_query):
    print(">>> DIREKT IM HAUPTMODUL: group_admin_handler wurde aufgerufen!", callback_query.data)
    await callback_query.answer("Direkter Handler (Gruppenverwaltung)!", show_alert=True)

print("[DEBUG] Handler-Registrierung in bot.py")
register_group_admin_menu_handlers(app, group_admin_menu, group_management)
print("[DEBUG] Handler-Registrierung abgeschlossen")

# Importiere die Handler-Registrierung, damit alle Menü-Handler aktiv sind
import bot.handlers.group_admin_menu_handlers
print("[DEBUG] bot.handlers.group_admin_menu_handlers importiert")

@app.on_message(filters.new_chat_members & filters.group)
async def handle_new_member(client, message):
    # Prüfen, ob der Bot selbst hinzugefügt wurde
    if any(u.is_self for u in message.new_chat_members):
        await group_management.on_bot_added_to_group(message)

# TriggerHandler initialisieren (z.B. mit None oder einer DB-Instanz)
trigger_handler = TriggerHandler(db=None)

@app.on_message(filters.group)
async def trigger_word_handler(client, message):
    text = message.text or message.caption
    if text:
        await trigger_handler.is_trigger(text, message)

# Bot starten
if __name__ == "__main__":
    logger.info("🚀 Telegram Bot wird gestartet...")
    app.run() 