import asyncio
import requests
from playwright.async_api import async_playwright

TELEGRAM_TOKEN = "8553987501:AAH_J85q0eUNUxPZCoW262X-GzBIrYzvGpM"
CHAT_ID = "7436219935"
SCAN_INTERVAL = 60

ALERTS = [
    {"name": "Levis 512", "query": "levis 512", "price_max": "70"},
    {"name": "G-Star", "query": "g star jeans", "price_max": "25"},
    {"name": "Diesel", "query": "diesel jeans", "price_max": "25"},
    {"name": "Armani", "query": "armani jeans", "price_max": "25"},
    {"name": "Ralph Lauren", "query": "ralph lauren jeans", "price_max": "25"},
    {"name": "Lee", "query": "lee jeans", "price_max": "25"},
]

seen_ids = set()

def send_telegram(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)
    except: pass

async def main():
    send_telegram("Bot demarre !")
    scan_count = 0
    while True:
        scan_count += 1
        print(f"Scan #{scan_count}")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await (await browser.new_context(locale="fr-FR")).new_page()
            await page.goto("https://www.vinted.fr", wait_until="domcontentloaded")
            await asyncio.sleep(3)
            for alert in ALERTS:
                try:
                    url = f"https://www.vinted.fr/api/v2/catalog/items?search_text={alert['query'].replace(' ','%20')}&order=newest_first&per_page=20&price_to={alert['price_max']}&catalog_ids[]=1206"
                    data = await page.evaluate(f"fetch('{url}',{{headers:{{'Accept':'application/json'}}}}).then(r=>r.json()).catch(e=>({{}}))")
                    items = data.get("items", []) if isinstance(data, dict) else []
                    print(f"  {alert['name']}: {len(items)} articles")
                    for item in items:
                        iid = item.get("id")
                        if iid and iid not in seen_ids:
                            seen_ids.add(iid)
                            if scan_count > 1:
                                send_telegram(f"<b>{alert['name']}</b>\n{item.get('title','')}\n{item.get('size_title','')}\n<b>{item.get('price_numeric','?')}EUR</b>\nhttps://www.vinted.fr/items/{iid}")
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"  Erreur {alert['name']}: {e}")
            await browser.close()
        if scan_count == 1:
            send_telegram("Premier scan OK ! Notifs activees.")
        await asyncio.sleep(SCAN_INTERVAL)

asyncio.run(main())
