from PIL import Image, ImageDraw, ImageFont

# Optional: Pfad zu einer TTF-Schriftart, z.B. DejaVuSans (systemweit meist vorhanden)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def make_market_image(data, fng, altseason):
    """
    Erzeugt ein PNG-Bild mit Marktdaten, Fear & Greed Index und Altcoin Season Index.
    data: dict mit Kursdaten (btc, eth, sol, bnb, doge, sui, trump)
    fng: (Wert, Klassifikation)
    altseason: int oder None
    Rückgabe: Pillow Image-Objekt
    """
    width, height = 800, 400
    img = Image.new("RGB", (width, height), (30, 30, 30))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_PATH, 36)
        small = ImageFont.truetype(FONT_PATH, 20)
    except Exception:
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    # Überschrift
    draw.text((30, 20), "Morning Market Update", font=font, fill=(255, 167, 38))

    # Kurse
    y = 80
    for key, label in zip([
        'btc', 'eth', 'sol', 'bnb', 'doge', 'sui', 'trump'],
        ['BTC', 'ETH', 'SOL', 'BNB', 'DOGE', 'SUI', 'TRUMP']):
        val = data.get(key, {})
        price = val.get('usd', '-')
        chg = val.get('usd_24h_change', '-')
        chg_str = f"{chg:+.2f}%" if isinstance(chg, (int, float)) else "-"
        draw.text((40, y), f"{label}: ${price} ({chg_str})", font=small, fill=(255,255,255))
        y += 32

    # Fear & Greed
    fng_val, fng_txt = fng if fng else ("-", "-")
    draw.text((40, y+10), f"Fear & Greed Index: {fng_val} ({fng_txt})", font=small, fill=(255, 167, 38))
    y += 42

    # Altcoin Season Index
    altseason_str = str(altseason) if altseason is not None else "-"
    draw.text((40, y+10), f"Altcoin Season Index: {altseason_str}", font=small, fill=(255, 167, 38))

    return img 