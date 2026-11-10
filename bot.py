import asyncio
import json
import os
import requests
from playwright.async_api import async_playwright

TELEGRAM_BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.environ.get('CHANNEL_ID')
AMAZON_NOW_URL = os.environ.get('AMAZON_URL')

DATA_FILE = 'amazon_now_prices.json'
COOKIES_FILE = 'cookies.json'

def load_json(filepath, default_val):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    return default_val

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

def send_telegram_alert(title, new_price, old_price, link):
    drop_amount = round(old_price - new_price, 2)
    message = (
        f"📉 *PRICE DROP ALERT* 📉\n\n"
        f"📦 {title}\n"
        f"💰 New Price: *₹{new_price}* (Dropped by ₹{drop_amount})\n"
        f"❌ Old Price: ~~₹{old_price}~~\n\n"
        f"🔗 🛒 [Grab it Fast!]({link})"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    requests.post(url, json=payload)

async def scan_amazon_now():
    price_database = load_json(DATA_FILE, {})
    updated_database = {}
    cookies = load_json(COOKIES_FILE, [])

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        if cookies:
            valid_cookies = [{k: v for k, v in c.items() if k in ['name', 'value', 'domain', 'path']} for c in cookies]
            await context.add_cookies(valid_cookies)

        page = await context.new_page()
        await page.goto(AMAZON_NOW_URL, wait_until="networkidle")

        products = await page.query_selector_all('div[data-asin]')

        for product in products:
            try:
                asin = await product.get_attribute('data-asin')
                if not asin: continue

                title_element = await product.query_selector('h2 a span')
                price_element = await product.query_selector('.a-price .a-offscreen')
                link_element = await product.query_selector('h2 a')

                if title_element and price_element and link_element:
                    title = await title_element.inner_text()
                    new_price = float((await price_element.inner_text()).replace('₹', '').replace(',', ''))
                    link = "https://www.amazon.in" + await link_element.get_attribute('href')

                    if asin in price_database:
                        old_price = price_database[asin]['price']
                        if new_price < old_price:
                            send_telegram_alert(title, new_price, old_price, link)
                    
                    updated_database[asin] = {"title": title, "price": new_price, "link": link}
            except Exception:
                continue

        await browser.close()
    
    price_database.update(updated_database)
    save_json(DATA_FILE, price_database)

if __name__ == "__main__":
    asyncio.run(scan_amazon_now())
