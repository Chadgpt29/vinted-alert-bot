import requests
import time
import random

TELEGRAM_TOKEN = "8553987501:AAH_J85q0eUNUxPZCoW262X-GzBIrYzvGpM"
CHAT_ID = "7436219935"
SCAN_INTERVAL = 120

ALERTS = [
    {"name": "Levi's 512", "query": "levis 512", "price_max": "70", "category": "1206"},
    {"name": "G-Star", "query": "g star jeans", "price_max": "25", "category": "1206"},
    {"name": "Ed Hardy", "query": "ed hardy jeans", "price_max": "25", "category": "1206"},
    {"name": "Dolce Gabbana", "query": "dolce gabbana jeans", "price_max": "25", "category": "1206"},
    {"name": "Diesel", "query": "diesel jeans", "price_max": "25", "category": "1206"},
    {"name": "Armani", "query": "armani jeans", "price_max": "25", "category": "1206"},
    {"name": "Ralph Lauren", "query": "ralph lauren jeans", "price_max": "25", "category": "1206"},
    {"name": "Lee", "query": "lee jeans", "price_max": "25", "category": "1206"},
    {"name": "Levi's 567", "query": "levis 567", "price_max": "25", "category": "1206"},
    {"name": "Marithe Girbaud", "query": "marithe girbaud jeans", "price_max": "25", "category": "1206"},
    {"name": "Maison Margiela", "query": "maison margiela jeans", "price_max": "25", "category": "1206"},
    {"name": "Teddy Smith", "query": "teddy smith jeans", "price_max": "25", "category": "1206"},
    {"name": "Hilfiger Denim", "query": "hilfiger denim jeans", "price_max": "25", "category": "1206"},
    {"name": "Camp David", "query": "camp david jeans", "price_max": "25", "category": "1206"},
    {"name": "Prada", "query": "prada jeans", "price_max": "25", "category": "1206"},
    {"name": "Coolcat", "query": "coolcat jeans", "price_max": "25", "category": "1206"},
    {"name": "Marithe Girbaud", "query": "marithe francois girbaud", "price_max": "25", "category": "1206"},
    {"name": "Revenue La Fam", "query": "revenue la fam jeans", "price_max": "25", "category": "1206"},
]

# User agents variés pour imiter de vrais navigateurs
USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 12; Samsung Galaxy S21) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
]

# Proxies gratuits publics à essayer
PROXY_LIST = [
    None,  # sans proxy d'abord
    {"http": "http://103.152.112.162:80", "https": "http://103.152.112.162:80"},
    {"http": "http://185.162.231.106:80", "https": "http://185.162.231.106:80"},
    {"http": "http://179.96.28.58:80", "https": "http://179.96.28.58:80"},
    {"http": "http://203.150.172.151:80", "https": "http://203.150.172.151:80"},
]

seen_ids = set()
working_proxy = None

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        print(f"Erreur Telegram: {e}")

def get_vinted_session():
    """Obtenir un cookie de session Vinted valide"""
    session = requests.Session()
    ua = random.choice(USER_AGENTS)
    session.headers.update({
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    })
    try:
        # Visiter la page principale pour obtenir les cookies
        resp = session.get("https://www.vinted.fr", timeout=15, proxies=working_proxy)
        print(f"  Session Vinted: HTTP {resp.status_code}")
        time.sleep(random.uniform(1, 3))
        return session
    except Exception as e:
        print(f"  Erreur session: {e}")
        return None

def scan_vinted(alert, session):
    url = (
        f"https://www.vinted.fr/api/v2/items"
        f"?search_text={requests.utils.quote(alert['query'])}"
        f"&order=newest_first&per_page=20"
        f"&price_to={alert.get('price_max','')}"
        f"&catalog_ids[]={alert.get('category','')}"
    )
    try:
        session.headers.update({
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.vinted.fr/vetements",
            "X-Requested-With": "XMLHttpRequest",
        })
        resp = session.get(url, timeout=15, proxies=working_proxy)
        print(f"  {alert['name']}: HTTP {resp.status_code}")
        if resp.status_code == 200:
            return resp.json().get("items", [])
        return []
    except Exception as e:
        print(f"  Erreur scan: {e}")
        return []

def run():
    global working_proxy
    print("Bot démarré !")
    send_telegram("🔄 Bot démarré — recherche d'une connexion valide vers Vinted...")

    # Tester les proxies
    for proxy in PROXY_LIST:
        try:
            label = str(proxy) if proxy else "sans proxy"
            print(f"Test proxy: {label}")
            session = requests.Session()
            session.headers["User-Agent"] = random.choice(USER_AGENTS)
            resp = session.get("https://www.vinted.fr/api/v2/items?search_text=levis&order=newest_first&per_page=5", 
                             proxies=proxy, timeout=10)
            if resp.status_code == 200 and resp.json().get("items"):
                working_proxy = proxy
                send_telegram(f"✅ Connexion trouvée ! Le bot surveille maintenant tes {len(ALERTS)} alertes 24h/24 !")
                print(f"Proxy fonctionnel: {label}")
                break
        except Exception as e:
            print(f"Proxy {label} KO: {e}")
            continue
    else:
        send_telegram("❌ Aucune connexion directe possible. Je vais quand même essayer toutes les minutes avec rotation d'identité...")

    scan_count = 0
    while True:
        scan_count += 1
        print(f"\n--- Scan #{scan_count} ---")

        session = get_vinted_session()
        if not session:
            time.sleep(30)
            continue

        total_new = 0
        for alert in ALERTS:
            items = scan_vinted(alert, session)
            for item in items:
                item_id = item.get("id")
                if item_id and item_id not in seen_ids:
                    seen_ids.add(item_id)
                    if scan_count > 1:
                        price = item.get("price_numeric") or item.get("price", "?")
                        title = item.get("title", "Sans titre")
                        size = item.get("size_title", "")
                        brand = item.get("brand_title", "")
                        url = f"https://www.vinted.fr/items/{item_id}"
                        msg = (
                            f"🔔 <b>{alert['name']}</b>\n"
                            f"👕 {title}\n"
                            f"🏷 {brand}\n"
                            f"📐 {size}\n"
                            f"💶 <b>{price}€</b>\n"
                            f"🔗 <a href='{url}'>Voir sur Vinted</a>"
                        )
                        send_telegram(msg)
                        total_new += 1
                        time.sleep(random.uniform(0.5, 1.5))
            time.sleep(random.uniform(1, 3))

        print(f"Scan #{scan_count} terminé — {total_new} nouveaux")
        time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    run()
