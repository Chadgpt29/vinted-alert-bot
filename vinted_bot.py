import requests
import time

TELEGRAM_TOKEN = "8553987501:AAH_J85q0eUNUxPZCoW262X-GzBIrYzvGpM"
CHAT_ID = "7436219935"
SCAN_INTERVAL = 60

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
]

seen_ids = set()

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        print(f"Erreur Telegram: {e}")

def scan_vinted(alert):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
        "Accept": "application/json",
        "Accept-Language": "fr-FR,fr;q=0.9",
        "Referer": "https://www.vinted.fr/",
    }
    url = f"https://www.vinted.fr/api/v2/items?search_text={requests.utils.quote(alert['query'])}&order=newest_first&per_page=20&price_to={alert.get('price_max','')}&catalog_ids[]={alert.get('category','')}"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"  {alert['name']}: HTTP {resp.status_code}")
        if resp.status_code == 200:
            return resp.json().get("items", [])
        else:
            print(f"  Réponse: {resp.text[:200]}")
            return []
    except Exception as e:
        print(f"  Erreur: {e}")
        return []

def run():
    print("Bot démarré !")
    send_telegram("✅ Bot démarré — test de connexion Vinted en cours...")
    
    # Test immédiat
    test = scan_vinted({"name": "Test", "query": "levis", "price_max": "50", "category": "1206"})
    if test:
        send_telegram(f"✅ Vinted répond ! {len(test)} articles trouvés pour 'levis'. Le bot va maintenant surveiller tes alertes.")
    else:
        send_telegram("❌ Vinted bloque les requêtes depuis ce serveur. Le bot ne peut pas fonctionner ainsi.")
    
    scan_count = 0
    while True:
        scan_count += 1
        print(f"\n--- Scan #{scan_count} ---")
        total_new = 0
        
        for alert in ALERTS:
            items = scan_vinted(alert)
            for item in items:
                item_id = item.get("id")
                if item_id and item_id not in seen_ids:
                    seen_ids.add(item_id)
                    if scan_count > 1:
                        price = item.get("price_numeric") or item.get("price", "?")
                        title = item.get("title", "Sans titre")
                        size = item.get("size_title", "")
                        url = f"https://www.vinted.fr/items/{item_id}"
                        msg = f"🔔 <b>{alert['name']}</b>\n👕 {title}\n📐 {size}\n💶 <b>{price}€</b>\n🔗 <a href='{url}'>Voir</a>"
                        send_telegram(msg)
                        total_new += 1
                        time.sleep(0.5)
            time.sleep(2)
        
        if scan_count == 2:
            send_telegram(f"📊 Scan #{scan_count} terminé — {total_new} nouveaux articles trouvés.")
        
        time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    run()
