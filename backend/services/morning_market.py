import requests
from bs4 import BeautifulSoup

def get_market_data():
    """
    Holt aktuelle Kursdaten für BTC, ETH, SOL, BNB, DOGE, SUI, TRUMP von CoinGecko.
    Gibt ein Dictionary mit Preisen und 24h-Änderungen zurück.
    """
    cg = requests.get(
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,binancecoin,dogecoin,sui,trump&vs_currencies=usd&include_24hr_change=true"
    ).json()
    return {
        'btc': cg['bitcoin'],
        'eth': cg['ethereum'],
        'sol': cg['solana'],
        'bnb': cg['binancecoin'],
        'doge': cg['dogecoin'],
        'sui': cg['sui'],
        'trump': cg.get('trump', {'usd': None, 'usd_24h_change': None}),
    }

def get_fear_greed():
    """
    Holt den aktuellen Fear & Greed Index von alternative.me.
    Gibt (Wert, Klassifikation) zurück.
    """
    r = requests.get("https://api.alternative.me/fng/")
    if r.ok:
        value = r.json()['data'][0]['value']
        classification = r.json()['data'][0]['value_classification']
        return int(value), classification
    return None, None

def get_altcoin_season_index():
    """
    Scraped den Altcoin Season Index von blockchaincenter.net.
    Gibt den Indexwert (int) zurück oder None bei Fehler.
    """
    try:
        url = "https://www.blockchaincenter.net/altcoin-season-index/"
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        span = soup.find("span", {"id": "main-index-value"})
        if span is not None:
            val = span.text
            return int(val)
        else:
            return None
    except Exception:
        return None 