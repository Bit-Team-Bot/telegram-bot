import aiohttp
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup  # type: ignore
from datetime import datetime
from zoneinfo import ZoneInfo

async def fetch_crypto_news():
    """Holt aktuelle Krypto-News von Cointelegraph (deutsch, RSS-Feed)."""
    url = "https://de.cointelegraph.com/rss"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=8) as resp:
                if resp.status != 200:
                    return "Fehler beim Abrufen der Krypto-News."
                xml_text = await resp.text()
                root = ET.fromstring(xml_text)
                items = root.findall('.//item')
                if not items:
                    return "Keine aktuellen Krypto-News gefunden."
                news_text = "🌐 **Krypto-News (Cointelegraph)**\n\n"
                for item in items[:5]:
                    title = item.findtext('title', default='')
                    link = item.findtext('link', default='')
                    news_text += f"• [{title}]({link})\n"
                return news_text
    except Exception as e:
        return f"Fehler beim Abrufen der Krypto-News: {e}"

async def fetch_joke():
    """Holt einen echten Witz von JokeAPI (deutsch, safe-mode)."""
    url = "https://v2.jokeapi.dev/joke/Any?lang=de&safe-mode"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=8) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("type") == "single":
                        return data.get("joke", "[Kein Witz gefunden]")
                    elif data.get("type") == "twopart":
                        return f"{data.get('setup', '')}\n{data.get('delivery', '')}"
                    else:
                        return "[Kein Witz gefunden]"
                else:
                    return "Fehler beim Abrufen des Witzes."
    except Exception as e:
        return f"Fehler beim Abrufen des Witzes: {e}"

def convert_time_to_berlin(timestr):
    """Konvertiert eine Uhrzeit (z.B. '15:30') von UTC nach Europe/Berlin."""
    try:
        dt_utc = datetime.combine(datetime.utcnow().date(), datetime.strptime(timestr, "%H:%M").time())
        dt_utc = dt_utc.replace(tzinfo=ZoneInfo("UTC"))
        dt_berlin = dt_utc.astimezone(ZoneInfo("Europe/Berlin"))
        return dt_berlin.strftime("%H:%M")
    except Exception:
        return timestr

async def fetch_economic_calendar():
    """Holt die wichtigsten Wirtschaftstermine von Investing.com (deutsch)."""
    url = "https://de.investing.com/economic-calendar/"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; TelegramBot/1.0)"
    }
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    return "Fehler beim Abrufen des Wirtschaftskalenders."
                html = await resp.text()
                soup = BeautifulSoup(html, "html.parser")  # type: ignore
                table = soup.find("table", {"id": "economicCalendarData"})  # type: ignore
                if not table:
                    return "Keine Termine gefunden."
                rows = table.find_all("tr", class_="js-event-item")  # type: ignore
                if not rows:
                    return "Keine Termine gefunden."
                events = []
                for row in rows[:8]:  # Zeige die nächsten 8 Termine
                    time_td = row.find("td", class_="first left time js-time")  # type: ignore
                    time = time_td.get_text(strip=True) if time_td else "-"
                    time_berlin = convert_time_to_berlin(time) if time != '-' else '-'
                    country_td = row.find("td", class_="left flagCur noWrap")  # type: ignore
                    country = ""
                    if country_td:
                        flag_span = row.find("span", class_="ceFlags")  # type: ignore
                        flag_attrs = getattr(flag_span, 'attrs', {}) if flag_span else {}
                        if 'title' in flag_attrs:
                            country = flag_attrs.get('title', '')
                    event_td = row.find("td", class_="left event")  # type: ignore
                    event = event_td.get_text(strip=True) if event_td else "-"
                    sentiment_td = row.find("td", class_="sentiment")  # type: ignore
                    sentiment_attrs = getattr(sentiment_td, 'attrs', {}) if sentiment_td else {}
                    impact = sentiment_attrs.get('title', '') if 'title' in sentiment_attrs else ""
                    events.append(f"{time_berlin} | {country} | {event} | {impact}")
                if not events:
                    return "Keine aktuellen Termine gefunden."
                text = "🗓️ **Nächste Wirtschaftstermine (Investing.com, Berlin-Zeit)**\n\n"
                text += "\n".join(f"• {e}" for e in events)
                text += "\n\n[Mehr Termine auf Investing.com](https://de.investing.com/economic-calendar/)"
                return text
    except Exception as e:
        return f"Fehler beim Abrufen des Wirtschaftskalenders: {e}" 