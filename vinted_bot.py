import requests
import time
import json

# ==============================
# CONFIG
# ==============================
TELEGRAM_TOKEN = "8553987501:AAH_J85q0eUNUxPZCoW262X-GzBIrYzvGpM"
CHAT_ID = "7436219935"
SCAN_INTERVAL = 60  # secondes entre chaque scan

# Tes alertes — modifie selon tes recherches
ALERTS = [
    {
        "name": "Levi's",
        "query": "levis",
        "size": "",       # ex: "S", "M", "L" ou "" pour toutes
        "price_max": "",  # ex: "50" ou "" pour pas de limite
        "category": "1206",  # 1206 = Pantalons & Jeans
    },
    {
        "name": "Nike Air Max",
        "query": "nike air max",
        "size": "",
        "price_max": "80",
        "category": "",
    },
    # Ajoute autant d'alertes que tu veux ici !
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
    send_telegram("✅ <b>VintedAlert Bot démarré !</b>\nJe vais te notifier dès qu'un nouvel article correspond à tes alertes.")
    
    scan_count = 0
    
    while True:
        scan_count += 1
        print(f"\n--- Scan #{scan_count} ---")
        
        for alert in ALERTS:
            print(f"🔍 Scan : {alert['name']}...")
            items = scan_vinted(alert)
            new_count = 0
            
            for item in items:
                item_id = item.get("id")
                if item_id and item_id not in seen_ids:
                    seen_ids.add(item_id)
                    if scan_count > 1:  # pas de notif au premier scan (évite le flood)
                        msg = format_message(item, alert["name"])
                        send_telegram(msg)
                        new_count += 1
                        time.sleep(0.5)  # petit délai entre les messages
            
            print(f"  → {len(items)} articles trouvés, {new_count} nouveaux")
            time.sleep(2)  # délai entre chaque alerte
        
        print(f"⏳ Prochain scan dans {SCAN_INTERVAL} secondes...")
        time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    run()
