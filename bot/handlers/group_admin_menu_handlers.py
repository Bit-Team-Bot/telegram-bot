import re
print("[DEBUG] group_admin_menu_handlers.py geladen")
# Handler für das Admin-Menü (aus register_group_admin_menu_handlers extrahiert)
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.client import Client
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ... BEGIN: Menü-Logik und Klasse GroupAdminMenu ...
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

class GroupAdminMenu:
    def __init__(self, client, get_group_settings, get_default_welcome_message):
        self.client = client
        self.get_group_settings = get_group_settings
        self.get_default_welcome_message = get_default_welcome_message
        self.pending_welcome_text = {}

    def get_admin_menu(self, chat_id, page=1):
        # Alle Menüeinträge als Liste
        menu_items = [
            ("👥 Mitglieder verwalten", f"admin_members_{chat_id}"),
            ("✉️ Begrüßungstext", f"admin_welcome_{chat_id}"),
            ("🌙 Nachtmodus", f"admin_nightmode_{chat_id}"),
            ("🔄 Weiterleitungen erlauben/verbieten", f"admin_forward_{chat_id}"),
            ("📅 Tägliche Info-Einstellungen", f"admin_info_settings_{chat_id}"),
            ("🔑 Rechte/Rollen", f"admin_roles_{chat_id}"),
            ("🤬 Beleidigungen verbieten", f"admin_badwords_{chat_id}"),
            ("🔗 Links erlauben/verbieten", f"admin_links_{chat_id}"),
            ("🛠️ DB-Test", f"admin_dbtest_{chat_id}"),
        ]
        items_per_page = 7
        total_pages = (len(menu_items) + items_per_page - 1) // items_per_page
        page = max(1, min(page, total_pages))
        start = (page - 1) * items_per_page
        end = start + items_per_page
        page_items = menu_items[start:end]
        keyboard = [[InlineKeyboardButton(text, callback_data=cb)] for text, cb in page_items]
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️ Vorherige Seite", callback_data=f"group_admin_{chat_id}_page_{page-1}"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("➡️ Nächste Seite", callback_data=f"group_admin_{chat_id}_page_{page+1}"))
        if nav_buttons:
            keyboard.append(nav_buttons)
        # Immer ein Zurück-Button
        keyboard.append([InlineKeyboardButton("🔙 Zurück", callback_data=f"menu_{chat_id}")])
        return InlineKeyboardMarkup(keyboard)

    def get_user_manage_menu(self, chat_id):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔇 User muten", callback_data=f"admin_mute_menu_{chat_id}")],
            [InlineKeyboardButton("⚠️ User verwarnen", callback_data=f"admin_warn_menu_{chat_id}")],
            [InlineKeyboardButton("👢 User kicken", callback_data=f"admin_kick_menu_{chat_id}")],
            [InlineKeyboardButton("🔙 Zurück", callback_data=f"group_admin_{chat_id}")]
        ])

    def get_back_to_admin_menu(self, chat_id):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Zurück", callback_data=f"group_admin_{chat_id}")]
        ])

    def get_back_to_user_manage_menu(self, chat_id):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Zurück", callback_data=f"user_manage_{chat_id}")]
        ])

    def get_group_main_menu(self, chat_id, is_admin=False):
        buttons = []
        if is_admin:
            cb = f"group_admin_{chat_id}"
            print("[DEBUG] Button-Callback-Data:", cb)
            buttons.append([InlineKeyboardButton("⚙️ Gruppenverwaltung", callback_data=cb)])
        cb_news = f"info_today_{chat_id}"
        print("[DEBUG] Button-Callback-Data:", cb_news)
        buttons.append([InlineKeyboardButton("📰 Krypto-News", callback_data=cb_news)])
        cb_cal = f"calendar_{chat_id}"
        print("[DEBUG] Button-Callback-Data:", cb_cal)
        buttons.append([InlineKeyboardButton("🗓️ Finanzkalender", callback_data=cb_cal)])
        cb_joke = f"joke_{chat_id}"
        print("[DEBUG] Button-Callback-Data:", cb_joke)
        buttons.append([InlineKeyboardButton("😂 Witze", callback_data=cb_joke)])
        cb_db = f"admin_dbtest_{chat_id}"
        print("[DEBUG] Button-Callback-Data:", cb_db)
        buttons.append([InlineKeyboardButton("🛠️ DB-Test", callback_data=cb_db)])
        return InlineKeyboardMarkup(buttons)

    async def handle_admin_nightmode_callback(self, callback_query):
        import re
        from bot.bot import backend_client
        chat_id_match = re.match(r"^admin_nightmode_(-?[0-9]+)$", callback_query.data)
        if not chat_id_match:
            await callback_query.answer("Ungültige Callback-Daten", show_alert=True)
            return
        chat_id = int(chat_id_match.group(1))
        # Status aus Backend holen
        try:
            group_data = backend_client.get(f"/groups/{chat_id}")
        except Exception as e:
            # Prüfe auf 'not found' und lege ggf. an
            error_str = str(e)
            if '404' in error_str or 'not found' in error_str.lower():
                # Gruppe anlegen
                try:
                    backend_client.post("/groups/", {
                        "group_id": str(chat_id),
                        "owner_id": callback_query.from_user.id,
                        "name": None
                    })
                    group_data = backend_client.get(f"/groups/{chat_id}")
                except Exception as e2:
                    await callback_query.edit_message_text(f"🌙 Nachtmodus\n\nFehler beim Anlegen der Gruppe: {e2}", reply_markup=self.get_back_to_admin_menu(chat_id))
                    return
            else:
                await callback_query.edit_message_text(f"🌙 Nachtmodus\n\nFehler beim Laden des Status: {e}", reply_markup=self.get_back_to_admin_menu(chat_id))
                return
        night_mode = group_data.get("night_mode", False)
        night_mode_start = group_data.get("night_mode_start") or "22:00"
        night_mode_end = group_data.get("night_mode_end") or "08:00"
        # Umschalt-Button
        toggle_text = "🌙 Nachtmodus: EIN" if night_mode else "🌙 Nachtmodus: AUS"
        toggle_button = InlineKeyboardButton(
            "Ausschalten" if night_mode else "Einschalten",
            callback_data=f"admin_nightmode_toggle_{chat_id}"
        )
        time_button = InlineKeyboardButton(
            f"Zeiten ändern ({night_mode_start}–{night_mode_end})",
            callback_data=f"admin_nightmode_timeedit_{chat_id}"
        )
        keyboard = [[toggle_button], [time_button], [InlineKeyboardButton("🔙 Zurück", callback_data=f"group_admin_{chat_id}")]]
        await callback_query.edit_message_text(
            f"🌙 <b>Nachtmodus</b>\n\nAktueller Status: <b>{'EIN' if night_mode else 'AUS'}</b>\nZeitraum: <b>{night_mode_start} – {night_mode_end}</b>\n\nIm Nachtmodus ist die Gruppe geschlossen und niemand kann schreiben.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # --- Nachtmodus-Zeiten ändern: Callback-Handler ---
    pending_nightmode_time = {}  # chat_id: {"step": 1/2, "start": None}

    @staticmethod
    def _is_valid_time(timestr):
        import re
        return bool(re.match(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", timestr))

# ... END: Menü-Logik und Klasse GroupAdminMenu ...

def register_group_admin_menu_handlers(app, group_admin_menu, group_management):
    from pyrogram import filters
    from pyrogram.types import Message, CallbackQuery

    @app.on_message(filters.command("menu") & filters.group)
    async def menu_command_handler(client, message):
        logger = logging.getLogger(__name__)
        logger.info(f"[DEBUG] menu_command_handler aufgerufen: chat_id={message.chat.id}, user_id={message.from_user.id}")
        chat_id = message.chat.id
        user_id = message.from_user.id
        print(f"[DEBUG] /menu Handler aufgerufen: chat_id={chat_id}, user_id={user_id}")
        try:
            member = await client.get_chat_member(chat_id, user_id)
            admin_status_values = ["creator", "administrator", "owner"]
            status_str = str(member.status).lower()
            is_admin = any(s in status_str for s in admin_status_values)
            print(f"[DEBUG] get_chat_member erfolgreich: status={status_str}, is_admin={is_admin}")
        except Exception as e:
            is_admin = False
            print(f"[DEBUG] get_chat_member Exception: {e}")
        keyboard = group_admin_menu.get_group_main_menu(chat_id, is_admin=is_admin)
        print(f"[DEBUG] Menü-Keyboard erzeugt: is_admin={is_admin}, keyboard={keyboard}")
        await message.reply("Gruppenmenü:", reply_markup=keyboard)

    @app.on_callback_query(filters.regex(r"^group_admin_-?[0-9]+(?:_page_-?[0-9]+)?$"))
    async def group_admin_handler(client, callback_query):
        logger = logging.getLogger(__name__)
        logger.info(f"[DEBUG] group_admin_handler aufgerufen: data={callback_query.data}")
        import re
        print(f"[DEBUG] group_admin_handler aufgerufen: data={callback_query.data}")
        m = re.match(r"^group_admin_(-?[0-9]+)(?:_page_(-?[0-9]+))?$", callback_query.data)
        if not m:
            print("[DEBUG] Callback-Regex passt nicht!")
            await callback_query.answer("❌ Ungültige Callback-Daten", show_alert=True)
            return
        chat_id = int(m.group(1))
        page = int(m.group(2)) if m.group(2) else 1
        print(f"[DEBUG] group_admin_handler: chat_id={chat_id}, page={page}")
        keyboard = group_admin_menu.get_admin_menu(chat_id, page=page)
        await callback_query.edit_message_text(
            "⚙️ **Gruppenverwaltung** (Seite {page})\n\nWähle eine Option:",
            reply_markup=keyboard
        )

    @app.on_callback_query(filters.regex(r"^admin_welcome_-?[0-9]+$"))
    async def admin_welcome_handler(client, callback_query):
        logger = logging.getLogger(__name__)
        logger.info(f"[DEBUG] admin_welcome_handler aufgerufen: data={callback_query.data}")
        print(f"[DEBUG] admin_welcome_handler aufgerufen: data={callback_query.data}")
        m = re.match(r"^admin_welcome_(-?[0-9]+)$", callback_query.data)
        if not m:
            await callback_query.answer("❌ Ungültige Callback-Daten", show_alert=True)
            return
        chat_id = int(m.group(1))
        try:
            from bot.bot import backend_client
            try:
                group_data = backend_client.get(f"/groups/{chat_id}")
            except Exception as e:
                error_str = str(e)
                if '404' in error_str or 'not found' in error_str.lower():
                    # Gruppe anlegen
                    backend_client.post("/groups/", {
                        "group_id": str(chat_id),
                        "owner_id": callback_query.from_user.id,
                        "name": None
                    })
            group_data = backend_client.get(f"/groups/{chat_id}")
                else:
                    raise
            welcome_text = group_data.get("welcome_text") or "Willkommen in der Gruppe!"
        except Exception as e:
            print(f"[DEBUG] Fehler beim Laden des Begrüßungstexts: {e}")
            welcome_text = "Willkommen in der Gruppe! (Fehler beim Laden aus Backend)"
        keyboard = [
            [InlineKeyboardButton("✏️ Bearbeiten", callback_data=f"admin_welcome_edit_{chat_id}")],
            [InlineKeyboardButton("🔙 Zurück", callback_data=f"group_admin_{chat_id}")]
        ]
        await callback_query.edit_message_text(
            f"✉️ **Begrüßungstext**\n\nAktueller Text:\n{welcome_text}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Pending-State für Admins, die gerade den Text bearbeiten
    pending_welcome_edit = {}

    @app.on_callback_query(filters.regex(r"^admin_welcome_edit_-?[0-9]+$"))
    async def admin_welcome_edit_handler(client, callback_query):
        logger = logging.getLogger(__name__)
        logger.info(f"[DEBUG] admin_welcome_edit_handler aufgerufen: data={callback_query.data}")
        print(f"[DEBUG] admin_welcome_edit_handler aufgerufen: data={callback_query.data}")
        m = re.match(r"^admin_welcome_edit_(-?[0-9]+)$", callback_query.data)
        if not m:
            await callback_query.answer("❌ Ungültige Callback-Daten", show_alert=True)
            return
        chat_id = int(m.group(1))
        admin_id = callback_query.from_user.id
        pending_welcome_edit[(admin_id, chat_id)] = True
        await callback_query.edit_message_text(
            "✏️ Sende jetzt den neuen Begrüßungstext als Nachricht.\n\nDu kannst Platzhalter wie {username} und {group_name} verwenden.\n\nAbbrechen: /cancel",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Zurück", callback_data=f"admin_welcome_{chat_id}")]
            ])
        )

    @app.on_message(filters.text & filters.group)
    async def handle_welcome_text_input(client, message):
        logger = logging.getLogger(__name__)
        logger.info(f"[DEBUG] handle_welcome_text_input aufgerufen: chat_id={message.chat.id}, user_id={message.from_user.id}, text={message.text}")
        chat_id = message.chat.id
        admin_id = message.from_user.id
        key = (admin_id, chat_id)
        if key not in pending_welcome_edit:
            return  # Kein Edit-Modus aktiv
        new_text = message.text.strip()
        if new_text.lower() == "/cancel":
            del pending_welcome_edit[key]
            await message.reply("❌ Bearbeitung abgebrochen.")
            return
        try:
            from bot.bot import backend_client
            backend_client.patch(f"/groups/{chat_id}", {"welcome_text": new_text})
            del pending_welcome_edit[key]
            await message.reply("✅ Begrüßungstext gespeichert!", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Zurück zum Admin-Menü", callback_data=f"group_admin_{chat_id}")]
            ]))
        except Exception as e:
            import traceback
            logger = logging.getLogger(__name__)
            logger.error(f"[DEBUG] Fehler beim Speichern des Begrüßungstexts: {e}\n{traceback.format_exc()}")
            await message.reply(f"❌ Fehler beim Speichern: {e}")

    @app.on_callback_query(filters.regex(r"^admin_members_-?[0-9]+(_page_\d+)?$"))
    async def admin_members_handler(client, callback_query):
        logger = logging.getLogger(__name__)
        logger.info(f"[DEBUG] admin_members_handler aufgerufen: data={callback_query.data}")
        import re
        print(f"[DEBUG] admin_members_handler aufgerufen: data={callback_query.data}")
        m = re.match(r"^admin_members_(-?[0-9]+)(?:_page_(\d+))?$", callback_query.data)
        if not m:
            await callback_query.answer("❌ Ungültige Callback-Daten", show_alert=True)
            return
        chat_id = int(m.group(1))
        page = int(m.group(2)) if m.group(2) else 1
        USERS_PER_PAGE = 20
        try:
            logger = logging.getLogger(__name__)
            logger.info(f"[DEBUG] Starte Mitglieder-Iteration für chat_id={chat_id}")
            members = []
            async for m in client.get_chat_members(chat_id):
                logger.info(f"[DEBUG] Gefundenes Mitglied: {getattr(m.user, 'id', None)} | Bot: {getattr(m.user, 'is_bot', None)} | Name: {getattr(m.user, 'first_name', None)}")
                if not m.user.is_bot:
                    members.append(m.user)
            logger.info(f"[DEBUG] Mitglieder-Liste fertig, Anzahl: {len(members)}")
            total = len(members)
            start = (page - 1) * USERS_PER_PAGE
            end = start + USERS_PER_PAGE
            page_members = members[start:end]
            logger.info(f"[DEBUG] Zeige Mitglieder von {start} bis {end} (Seite {page})")
            keyboard = []
            for user in page_members:
                logger.info(f"[DEBUG] Baue Button für User: {user.id} | Name: {user.first_name} {user.last_name} | Username: {user.username}")
                name = user.first_name or "User"
                if user.last_name:
                    name += f" {user.last_name}"
                if user.username:
                    name += f" (@{user.username})"
                keyboard.append([InlineKeyboardButton(name, callback_data=f"admin_useraction_{chat_id}_{user.id}")])
            nav_buttons = []
            if page > 1:
                nav_buttons.append(InlineKeyboardButton("⬅️ Zurück", callback_data=f"admin_members_{chat_id}_page_{page-1}"))
            if end < total:
                nav_buttons.append(InlineKeyboardButton("➡️ Weiter", callback_data=f"admin_members_{chat_id}_page_{page+1}"))
            if nav_buttons:
                keyboard.append(nav_buttons)
            keyboard.append([InlineKeyboardButton("🔙 Zurück", callback_data=f"group_admin_{chat_id}")])
            logger.info(f"[DEBUG] Sende Mitglieder-Menü an Telegram...")
            await callback_query.edit_message_text(
                f"👥 **Mitglieder verwalten** (Seite {page})\nWähle ein Mitglied:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            logger.info(f"[DEBUG] Mitglieder-Menü erfolgreich gesendet.")
        except Exception as e:
            logger.error(f"[DEBUG] Fehler beim Laden der Mitglieder: {e}")
            await callback_query.answer("Fehler beim Laden der Mitglieder", show_alert=True)

    @app.on_callback_query(filters.regex(r"^admin_useraction_-?[0-9]+_\d+$"))
    async def admin_useraction_handler(client, callback_query):
        logger = logging.getLogger(__name__)
        logger.info(f"[DEBUG] admin_useraction_handler aufgerufen: data={callback_query.data}")
        print(f"[DEBUG] admin_useraction_handler aufgerufen: data={callback_query.data}")
        m = re.match(r"^admin_useraction_(-?[0-9]+)_(\d+)$", callback_query.data)
        if not m:
            await callback_query.answer("❌ Ungültige Callback-Daten", show_alert=True)
            return
        chat_id = int(m.group(1))
        user_id = int(m.group(2))
        # Menü für Aktionen anzeigen
        keyboard = [
            [InlineKeyboardButton("🔇 User muten", callback_data=f"admin_mute_{chat_id}_{user_id}")],
            [InlineKeyboardButton("⚠️ User verwarnen", callback_data=f"admin_warn_{chat_id}_{user_id}")],
            [InlineKeyboardButton("👢 User kicken", callback_data=f"admin_kick_{chat_id}_{user_id}")],
            [InlineKeyboardButton("🔙 Zurück", callback_data=f"admin_members_{chat_id}")]
        ]
        await callback_query.edit_message_text(
            f"Wähle eine Aktion für User {user_id}:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    @app.on_callback_query(filters.regex(r"^admin_nightmode_toggle_[0-9]+$"))
    async def admin_nightmode_toggle_handler(client, callback_query):
        import re
        from bot.bot import backend_client
        chat_id_match = re.match(r"^admin_nightmode_toggle_(-?[0-9]+)$", callback_query.data)
        if not chat_id_match:
            await callback_query.answer("Ungültige Callback-Daten", show_alert=True)
            return
        chat_id = int(chat_id_match.group(1))
        try:
            group_data = backend_client.get(f"/groups/{chat_id}")
            night_mode = group_data.get("night_mode", False)
            # Umschalten
            new_status = not night_mode
            backend_client.patch(f"/groups/{chat_id}", {"night_mode": new_status})
            # Rückmeldung
            status_text = 'EIN' if new_status else 'AUS'
            toggle_button = InlineKeyboardButton(
                "Ausschalten" if new_status else "Einschalten",
                callback_data=f"admin_nightmode_toggle_{chat_id}"
            )
            keyboard = [[toggle_button], [InlineKeyboardButton("🔙 Zurück", callback_data=f"group_admin_{chat_id}")]]
            await callback_query.edit_message_text(
                f"🌙 <b>Nachtmodus</b>\n\nAktueller Status: <b>{status_text}</b>\n\nIm Nachtmodus ist die Gruppe geschlossen und niemand kann schreiben.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            await callback_query.edit_message_text(f"🌙 Nachtmodus\n\nFehler beim Umschalten: {e}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Zurück", callback_data=f"group_admin_{chat_id}")]]))

    @app.on_callback_query(filters.regex(r"^admin_forward_[0-9]+$"))
    async def admin_forward_handler(client, callback_query):
        try:
            await callback_query.answer()
            await group_admin_menu.handle_admin_forward_callback(callback_query)
        except Exception as e:
            await callback_query.answer(str(e), show_alert=True)

    @app.on_callback_query(filters.regex(r"^admin_info_settings_[0-9]+$"))
    async def admin_info_settings_handler(client, callback_query):
        try:
            await callback_query.answer()
            await group_admin_menu.handle_admin_info_settings_callback(callback_query)
        except Exception as e:
            await callback_query.answer(str(e), show_alert=True)

    @app.on_callback_query(filters.regex(r"^admin_badwords_[0-9]+$"))
    async def admin_badwords_handler(client, callback_query):
        try:
            await callback_query.answer()
            await group_admin_menu.handle_admin_badwords_callback(callback_query)
        except Exception as e:
            await callback_query.answer(str(e), show_alert=True)

    @app.on_callback_query(filters.regex(r"^admin_links_[0-9]+$"))
    async def admin_links_handler(client, callback_query):
        try:
            await callback_query.answer()
            await group_admin_menu.handle_admin_links_callback(callback_query)
        except Exception as e:
            await callback_query.answer(str(e), show_alert=True)

    @app.on_callback_query(filters.regex(r"^info_today_-?[0-9]+$"))
    async def info_today_handler(client, callback_query):
        print(f"[DEBUG] info_today_handler aufgerufen: data={callback_query.data}")
        await callback_query.answer()
        from bot.bot_utils import fetch_crypto_news
        news_text = await fetch_crypto_news()
        await callback_query.edit_message_text(news_text)

    @app.on_callback_query(filters.regex(r"^joke_-?[0-9]+$"))
    async def joke_handler(client, callback_query):
        print(f"[DEBUG] joke_handler aufgerufen: data={callback_query.data}")
        await callback_query.answer()
        from bot.bot_utils import fetch_joke
        joke_text = await fetch_joke()
        await callback_query.edit_message_text(joke_text)

    @app.on_callback_query(filters.regex(r"^calendar_-?[0-9]+$"))
    async def calendar_handler(client, callback_query):
        print(f"[DEBUG] calendar_handler aufgerufen: data={callback_query.data}")
        await callback_query.answer()
        from bot.bot_utils import fetch_economic_calendar
        text = await fetch_economic_calendar()
        await callback_query.edit_message_text(text, disable_web_page_preview=False)

    @app.on_callback_query(filters.regex(r"^admin_dbtest_-?[0-9]+$"))
    async def admin_dbtest_handler(client, callback_query):
        print(f"[DEBUG] admin_dbtest_handler aufgerufen: data={callback_query.data}")
        await callback_query.answer()
        await callback_query.edit_message_text("🛠️ **DB-Test**\n\nDie Datenbankverbindung funktioniert!")

    @app.on_callback_query(filters.regex(r"^admin_mute_-?[0-9]+_\d+$"))
    async def admin_mute_handler(client, callback_query):
        print(f"[DEBUG] admin_mute_handler aufgerufen: data={callback_query.data}")
        m = re.match(r"^admin_mute_(-?[0-9]+)_(\d+)$", callback_query.data)
        if not m:
            await callback_query.answer("❌ Ungültige Callback-Daten", show_alert=True)
            return
        chat_id = int(m.group(1))
        user_id = int(m.group(2))
        admin_id = callback_query.from_user.id
        try:
            from pyrogram.types import ChatPermissions
            from datetime import datetime, timedelta
            from bot.bot import backend_client
            duration_seconds = 5 * 60  # 5 Minuten
            until_date = datetime.utcnow() + timedelta(seconds=duration_seconds)
            await client.restrict_chat_member(
                chat_id,
                user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until_date
            )
            keyboard = [
                [InlineKeyboardButton("🔙 Zurück", callback_data=f"admin_members_{chat_id}")]
            ]
            await callback_query.edit_message_text(
                f"🔇 User {user_id} wurde für 5 Minuten gemutet.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            print(f"[DEBUG] Fehler beim Muten: {e}")
            await callback_query.answer("Fehler beim Muten", show_alert=True)

    @app.on_callback_query(filters.regex(r"^admin_warn_-?[0-9]+_\d+$"))
    async def admin_warn_handler(client, callback_query):
        print(f"[DEBUG] admin_warn_handler aufgerufen: data={callback_query.data}")
        m = re.match(r"^admin_warn_(-?[0-9]+)_(\d+)$", callback_query.data)
        if not m:
            await callback_query.answer("❌ Ungültige Callback-Daten", show_alert=True)
            return
        chat_id = int(m.group(1))
        user_id = int(m.group(2))
        admin_id = callback_query.from_user.id
        try:
            from bot.bot import backend_client
            # Backend-API-Call zum Speichern der Verwarnung
            try:
                backend_client.post("/group_warnings/", {
                    "user_id": user_id,
                    "group_id": chat_id,
                    "reason": "Verwarnung durch Admin-Menü",
                    "issued_by": admin_id
                })
            except Exception as e:
                print(f"[DEBUG] Fehler beim Speichern der Verwarnung im Backend: {e}")
            await client.send_message(chat_id, f"⚠️ User [{user_id}](tg://user?id={user_id}) wurde verwarnt.")
            keyboard = [
                [InlineKeyboardButton("🔙 Zurück", callback_data=f"admin_members_{chat_id}")]
            ]
            await callback_query.edit_message_text(
                f"⚠️ User {user_id} wurde verwarnt.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            print(f"[DEBUG] Fehler beim Verwarnen: {e}")
            await callback_query.answer("Fehler beim Verwarnen", show_alert=True)

    @app.on_callback_query(filters.regex(r"^admin_kick_-?[0-9]+_\d+$"))
    async def admin_kick_handler(client, callback_query):
        print(f"[DEBUG] admin_kick_handler aufgerufen: data={callback_query.data}")
        m = re.match(r"^admin_kick_(-?[0-9]+)_(\d+)$", callback_query.data)
        if not m:
            await callback_query.answer("❌ Ungültige Callback-Daten", show_alert=True)
            return
        chat_id = int(m.group(1))
        user_id = int(m.group(2))
        admin_id = callback_query.from_user.id
        try:
            from bot.bot import backend_client
            await client.ban_chat_member(chat_id, user_id)
            # Backend-API-Call zum Speichern des Kicks/Bans
            try:
                backend_client.post("/group_kicks/", {
                    "user_id": user_id,
                    "group_id": chat_id,
                    "reason": "Kick/Ban durch Admin-Menü",
                    "issued_by": admin_id
                })
            except Exception as e:
                print(f"[DEBUG] Fehler beim Speichern des Kicks im Backend: {e}")
            keyboard = [
                [InlineKeyboardButton("🔙 Zurück", callback_data=f"admin_members_{chat_id}")]
            ]
            await callback_query.edit_message_text(
                f"👢 User {user_id} wurde aus der Gruppe entfernt.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            print(f"[DEBUG] Fehler beim Kicken: {e}")
            await callback_query.answer("Fehler beim Kicken", show_alert=True)

    @app.on_callback_query(filters.regex(r"^admin_nightmode_timeedit_[0-9]+$"))
    async def admin_nightmode_timeedit_handler(client, callback_query):
        import re
        chat_id_match = re.match(r"^admin_nightmode_timeedit_(-?[0-9]+)$", callback_query.data)
        if not chat_id_match:
            await callback_query.answer("Ungültige Callback-Daten", show_alert=True)
            return
        chat_id = int(chat_id_match.group(1))
        group_admin_menu.pending_nightmode_time[chat_id] = {"step": 1, "start": None}
        await callback_query.message.reply_text(
            "Bitte gib die <b>Startzeit</b> für den Nachtmodus im Format HH:MM an (z.B. 22:00):",
            parse_mode="html"
        )
        await callback_query.answer()

    @app.on_message(filters.text & filters.group)
    async def handle_nightmode_time_input(client, message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        # Prüfen, ob wir auf eine Zeit warten
        if chat_id not in group_admin_menu.pending_nightmode_time:
            return  # Kein Zeit-Dialog offen
        state = group_admin_menu.pending_nightmode_time[chat_id]
        text = message.text.strip()
        if state["step"] == 1:
            if not GroupAdminMenu._is_valid_time(text):
                await message.reply("❌ Ungültiges Format! Bitte gib die Startzeit im Format HH:MM an (z.B. 22:00):")
                return
            state["start"] = text
            state["step"] = 2
            await message.reply("Bitte gib die <b>Endzeit</b> für den Nachtmodus im Format HH:MM an (z.B. 08:00):", parse_mode="html")
        elif state["step"] == 2:
            if not GroupAdminMenu._is_valid_time(text):
                await message.reply("❌ Ungültiges Format! Bitte gib die Endzeit im Format HH:MM an (z.B. 08:00):")
                return
            start = state["start"]
            end = text
            from bot.bot import backend_client
            try:
                backend_client.patch(f"/groups/{chat_id}", {"night_mode_start": start, "night_mode_end": end})
                await message.reply(f"🌙 Nachtmodus-Zeiten gespeichert: {start} – {end}")
            except Exception as e:
                await message.reply(f"Fehler beim Speichern im Backend: {e}")
            del group_admin_menu.pending_nightmode_time[chat_id]
            # Menü aktualisieren
            await group_admin_menu.handle_admin_nightmode_callback(await client.get_chat(chat_id))

    # ... weitere Handler für alle Untermenüs und Aktionen analog ergänzen ... 