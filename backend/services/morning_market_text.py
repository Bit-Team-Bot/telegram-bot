TEMPLATES = {
    "de": """
📊 Marktlage am Morgen

- BTC ≈${btc} ({btc_chg})
- ETH ≈${eth} ({eth_chg})
- SOL ≈${sol} ({sol_chg})
- BNB ≈${bnb} ({bnb_chg})
- DOGE ≈${doge} ({doge_chg})
- SUI ≈${sui} ({sui_chg})
- TRUMP ≈${trump} ({trump_chg})

- Fear & Greed Index: {fng} ({fng_txt})
- Altseason Index: {altseason}
""",
    "en": """
📊 Morning market conditions

- BTC ≈${btc} ({btc_chg})
- ETH ≈${eth} ({eth_chg})
- SOL ≈${sol} ({sol_chg})
- BNB ≈${bnb} ({bnb_chg})
- DOGE ≈${doge} ({doge_chg})
- SUI ≈${sui} ({sui_chg})
- TRUMP ≈${trump} ({trump_chg})

- Fear and Greed Index: {fng} ({fng_txt})
- Altseason index: {altseason}
""",
    "ru": """
📊 Утренний обзор рынка

- BTC ≈${btc} ({btc_chg})
- ETH ≈${eth} ({eth_chg})
- SOL ≈${sol} ({sol_chg})
- BNB ≈${bnb} ({bnb_chg})
- DOGE ≈${doge} ({doge_chg})
- SUI ≈${sui} ({sui_chg})
- TRUMP ≈${trump} ({trump_chg})

- Индекс страха и жадности: {fng} ({fng_txt})
- Altseason-индекс: {altseason}
"""
}

def make_market_text(data, fng, altseason, lang="de"):
    """
    Baut den Morning Market Text in der gewünschten Sprache.
    data: dict mit Kursdaten
    fng: (Wert, Klassifikation)
    altseason: int oder None
    lang: 'de', 'en', 'ru'
    Rückgabe: formatierter Text
    """
    template = TEMPLATES.get(lang, TEMPLATES["en"])
    def fmt(val):
        return f"{val:.2f}" if isinstance(val, (int, float)) else "-"
    def fmt_chg(val):
        return f"{val:+.2f}%" if isinstance(val, (int, float)) else "-"
    d = {
        'btc': fmt(data.get('btc', {}).get('usd')),
        'btc_chg': fmt_chg(data.get('btc', {}).get('usd_24h_change')),
        'eth': fmt(data.get('eth', {}).get('usd')),
        'eth_chg': fmt_chg(data.get('eth', {}).get('usd_24h_change')),
        'sol': fmt(data.get('sol', {}).get('usd')),
        'sol_chg': fmt_chg(data.get('sol', {}).get('usd_24h_change')),
        'bnb': fmt(data.get('bnb', {}).get('usd')),
        'bnb_chg': fmt_chg(data.get('bnb', {}).get('usd_24h_change')),
        'doge': fmt(data.get('doge', {}).get('usd')),
        'doge_chg': fmt_chg(data.get('doge', {}).get('usd_24h_change')),
        'sui': fmt(data.get('sui', {}).get('usd')),
        'sui_chg': fmt_chg(data.get('sui', {}).get('usd_24h_change')),
        'trump': fmt(data.get('trump', {}).get('usd')),
        'trump_chg': fmt_chg(data.get('trump', {}).get('usd_24h_change')),
        'fng': fng[0] if fng else '-',
        'fng_txt': fng[1] if fng else '-',
        'altseason': altseason if altseason is not None else '-',
    }
    return template.format(**d) 