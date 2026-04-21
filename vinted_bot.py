import requests
import time

# ==============================
# CONFIG
# ==============================
TELEGRAM_TOKEN = "8553987501:AAH_J85q0eUNUxPZCoW262X-GzBIrYzvGpM"
CHAT_ID = "7436219935"
SCAN_INTERVAL = 60  # secondes entre chaque scan

ALERTS = [
    {
        "name": "Levi's 512",
        "query": "levis 512",
        "size": "",
        "price_max": "70",
        "category": "1206",
    },
    {
        "name": "G-Star",
        "query": "g star jeans pantalon",
        "size": "",
        "price_max": "25",
        "category": "1206",
    },
    {
        "name": "Ed Hardy",
        "query": "ed hardy jeans pantalon",
        "size": "",
        "price_max": "25",
        "category": "1206",
    },
    {
        "name": "Dolce & Gabbana",
        "query": "dolce gabbana jeans pantalon",
        "size": "",
        "price_max": "25",
        "category": "1206",
    },
    {
        "name": "Hilfiger Denim",
        "query": "hilfiger denim jeans pantalon",
        "size": "",
        "price_max": "25",
        "category": "1206",
    },
    {
        "name": "Diesel",
        "query": "diesel jeans pantalon",
        "size": "",
        "price_max": "25",
        "category": "1206",
    },
    {
        "name": "Armani",
        "query": "armani jeans pantalon",
        "size": "",
        "price_max": "25",
        "category": "1206",
    },
    {
        "name": "Camp David",
        "query": "camp david jeans pantalon",
        "size": "",
        "price_max": "25",
        "category": "1206",
    },
    {
        "name": "Prada",
        "query": "prada jeans pantalon",
        "size": "",
        "price_max": "25",
        "category": "1206",
    },
    {
        "name": "Baggy Pants",
        "query": "baggy pants jeans",
        "size": "",
        "price_max": "25",
        "category": "1206",
    },
    {
        "name": "Levi's 567 Loose Boot Cut",
        "query": "levis 567 loose boot cut",
        "size": "",
        "price_max": "25",
        "category": "1206",
    },
    {
        "name": "Revenue La Fam",
        "query": "revenue la fam jeans",
        "size": "",
        "price_max": "25",
        "category": "1206",
    },
    {
        "name": "Teddy Smith",
        "query": "teddy smith jeans pantalon",
        "size": "",
        "price_max": "25",
        "category": "1206",
    },
    {
        "name": "Coolcat",
        "query": "coolcat jeans pantalon",
        "size": "",
        "price_max": "25",
        "category": "1206",
    },
    {
        "name": "Ralph Lauren",
        "query": "ralph lauren jeans pantalon",
        "size": "",
        "price_max": "25",
        "category": "1206",
    },
    {
        "name": "Marithe Girbaud",
        "query": "marithe francois girbaud jeans",
        "size": "",
        "price_max": "25",
        "category": "1206",
    },
    {
        "name": "Maison Margiela",
        "query": "maison margiela jeans pantalon",
        "size": "",
        "price_max": "25",
        "category": "1206",
    },
    {
        "name": "Lee",
        "query": "lee jeans pantalon",
        "size": "",
        "price_max": "25",
        "category": "1206",
    },
]

# ==============================
# FONCTIONS
# ==============================

seen_ids = set()

def build_url(alert):
    url = f"https://www.vinted.fr/api/v2/items?search_text={requests.utils.quote(alert['query'])}&order=newest_first&per_page=20"
    if alert.get("price_max"):
        url += f"&price_to={alert['price_max']}"
    if alert.get("category"):
        url += f"&catalog_ids[]={alert['category']}"
    return url

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Erreur Telegram: {e}")

def scan_vinted(alert):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "fr-FR,fr;q=0.9",
        "Referer": "https://www.vinted.fr/",
        "X-Requested-With": "XMLHttpRequest",
    }
    try:
        url = build_url(alert)
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            print(f"Erreur HTTP {resp.status_code} pour {alert['name']}")
            return []
        data = resp.json()
        return data.get("items", [])
    except Exception as e:
        print(f"Erreur scan {alert['name']}: {e}")
        return []

def format_message(item, alert_name):
    title = item.get("title", "Article sans titre")
    price = item.get("price_numeric") or item.get("price", "?")
    size = item.get("size_title", "")
    brand = item.get("brand_title", "")
    url = f"https://www.vinted.fr/items/{item['id']}"
    
    msg = f"🔔 <b>Nouvelle annonce — {alert_name}</b>\n\n"
    msg += f"👕 <b>{title}</b>\n"
    if brand:
        msg += f"🏷 Marque : {brand}\n"
    if size:
        msg += f"📐 Taille : {size}\n"
    msg += f"💶 Prix : <b>{price} €</b>\n"
    msg += f"\n🔗 <a href='{url}'>Voir l'article</a>"
    return msg

def run():
    print("🚀 VintedAlert Bot démarré !")
    send_telegram("✅ <b>VintedAlert Bot démarré !</b>\nJe surveille 18 marques de jeans/pantalons pour toi 24h/24 !")
    
    scan_count = 0
    
    while True:
        scan_count += 1
        print(f"\n--- Scan #{scan_count} ---")
        
        for alert in ALERTS:
            print(f"Scan : {alert['name']}...")
            items = scan_vinted(alert)
            new_count = 0
            
            for item in items:
                item_id = item.get("id")
                if item_id and item_id not in seen_ids:
                    seen_ids.add(item_id)
                    if scan_count > 1:
                        msg = format_message(item, alert["name"])
                        send_telegram(msg)
                        new_count += 1
                        time.sleep(0.5)
            
            print(f"  -> {len(items)} articles, {new_count} nouveaux")
            time.sleep(2)
        
        print(f"Prochain scan dans {SCAN_INTERVAL} secondes...")
        time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    run()
