import asyncio
import requests
from playwright.async_api import async_playwright

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
    {"name": "Hilfiger Denim", "query": "hilfiger denim jeans", "price_max": "25", "category": "1206"},
    {"name": "Camp David", "query": "camp david jeans", "price_max": "25", "category": "1206"},
    {"name": "Prada", "query": "prada jeans", "price_max": "25", "category": "1206"},
    {"name": "Coolcat", "query": "coolcat jeans", "price_max": "25", "category": "1206"},
    {"name": "Revenue La Fam", "query": "revenue la fam jeans", "price_max": "25", "category": "1206"},
]

seen_ids = set()

def send_telegram(message):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        print(f"Erreur Telegram: {e}")

async def scan_all():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            locale="fr-FR",
            viewport={"width": 390, "height": 844}
        )
        page = await context.new_page()
        print("Chargement de Vinted...")
        await page.goto("https://www.vinted.fr", wait_until="domcontentloaded")
        await asyncio.sleep(3)

        items_found = []
        for alert in ALERTS:
            try:
                url = (f"https://www.vinted.fr/api/v2/catalog/items"
                       f"?search_text={alert['query'].replace(' ', '%20')}"
                       f"&order=newest_first&per_page=20"
                       f"&price_to={alert.get('price_max','')}"
                       f"&catalog_ids[]={alert.get('category','')}")
                response = await page.evaluate(f"""
                    fetch('{url}', {{
                        headers: {{
                            'Accept': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest'
                        }}
                    }}).then(r => r.json()).catch(e => ({{'error': e.toString()}}))
                """)
                if isinstance(response, dict) and "items" in response:
                    items = response["items"]
                    print(f"  {alert['name']}: {len(items)} articles")
                    for item in items:
                        items_found.append((item, alert["name"]))
                else:
                    print(f"  {alert['name']}: pas de resultats")
                await asyncio.sleep(1)
            except Exception as e:
                print(f"  {alert['name']}: erreur {e}")

        await browser.close()
        return items_found

async def main():
    print("Bot Playwright demarre !")
    send_telegram("Demarrage du bot avec vrai navigateur...")

    scan_count = 0
    while True:
        scan_count += 1
        print(f"\n--- Scan #{scan_count} ---")
        try:
            results = await scan_all()
            new_count = 0
            for item, alert_name in results:
                item_id = item.get("id")
                if item_id and item_id not in seen_ids:
                    seen_ids.add(item_id)
                    if scan_count > 1:
                        price = item.get("price_numeric") or item.get("price", "?")
                        title = item.get("title", "Sans titre")
                        size = item.get("size_title", "")
                        brand = item.get("brand_title", "")
                        url = f"https://www.vinted.fr/items/{item_id}"
                        msg = (f"Nouvelle annonce - {alert_name}\n"
                               f"{title}\n"
                               f"{brand} - {size}\n"
                               f"{price} EUR\n"
                               f"https://www.vinted.fr/items/{item_id}")
                        send_telegram(msg)
                        new_count += 1
                        await asyncio.sleep(0.5)
            if scan_count == 1:
                if results:
                    send_telegram(f"Ca marche ! {len(results)} articles trouves au premier scan. Les notifs arrivent des qu'il y a du nouveau !")
                else:
                    send_telegram("Premier scan termine - 0 articles. Quelque chose cloche...")
            print(f"Scan #{scan_count} - {new_count} nouveaux")
        except Exception as e:
            print(f"Erreur: {e}")
        await asyncio.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())
