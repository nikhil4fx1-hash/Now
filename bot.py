import asyncio
import json
import os
import requests
from playwright.async_api import async_playwright

TELEGRAM_BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.environ.get('CHANNEL_ID')

AMAZON_NOW_URLS = [
    "https://www.amazon.in/tez/browse/explore/collection?qcbrand=qqfsWw9RkO&nodeId=204924538031&title=Beverages&pf_rd_r=7F1RMR5CT7GKWBHXN921&pf_rd_p=843e77b6-8834-4ef1-bf3b-ecc146b1b1bb",
    "https://www.amazon.in/tez/browse/explore/collection?qcbrand=qqfsWw9RkO&nodeId=215540425031&title=Snacks+%26+Treats&pf_rd_r=7F1RMR5CT7GKWBHXN921&pf_rd_p=843e77b6-8834-4ef1-bf3b-ecc146b1b1bb",
    "https://www.amazon.in/tez/browse/explore/collection?qcbrand=qqfsWw9RkO&nodeId=204992653031&title=Bath+%26+Body&pf_rd_r=7F1RMR5CT7GKWBHXN921&pf_rd_p=843e77b6-8834-4ef1-bf3b-ecc146b1b1bb",
    "https://www.amazon.in/tez/browse/explore/collection?qcbrand=qqfsWw9RkO&nodeId=204952388031&title=Cleaners&pf_rd_r=7F1RMR5CT7GKWBHXN921&pf_rd_p=843e77b6-8834-4ef1-bf3b-ecc146b1b1bb",
    "https://www.amazon.in/tez/browse/explore/collection?qcbrand=qqfsWw9RkO&nodeId=204952381031&title=Dishwash+%26+Detergents&pf_rd_r=7F1RMR5CT7GKWBHXN921&pf_rd_p=843e77b6-8834-4ef1-bf3b-ecc146b1b1bb",
    "https://www.amazon.in/tez/browse/explore/collection?qcbrand=qqfsWw9RkO&nodeId=204869998031&title=Dairy+%26+Bread&pf_rd_r=7F1RMR5CT7GKWBHXN921&pf_rd_p=843e77b6-8834-4ef1-bf3b-ecc146b1b1bb",
    "https://www.amazon.in/tez/browse/explore/collection?qcbrand=qqfsWw9RkO&nodeId=220619214031&title=Fruits&pf_rd_r=7F1RMR5CT7GKWBHXN921&pf_rd_p=843e77b6-8834-4ef1-bf3b-ecc146b1b1bb",
    "https://www.amazon.in/tez/browse/explore/collection?qcbrand=qqfsWw9RkO&nodeId=218833871031&title=Vegetables&pf_rd_r=7F1RMR5CT7GKWBHXN921&pf_rd_p=843e77b6-8834-4ef1-bf3b-ecc146b1b1bb",
    "https://www.amazon.in/tez/browse/explore/collection?qcbrand=qqfsWw9RkO&nodeId=204992619031&title=Men%2527s+Grooming&pf_rd_r=7F1RMR5CT7GKWBHXN921&pf_rd_p=843e77b6-8834-4ef1-bf3b-ecc146b1b1bb",
    "https://www.amazon.in/tez/browse/explore/collection?qcbrand=qqfsWw9RkO&nodeId=205015896031&title=Nutrition+%26+Protein&pf_rd_r=7F1RMR5CT7GKWBHXN921&pf_rd_p=843e77b6-8834-4ef1-bf3b-ecc146b1b1bb",
    "https://www.amazon.in/tez/browse/explore/collection?qcbrand=qqfsWw9RkO&nodeId=204924535031&title=Tea+%26+Coffee&pf_rd_r=7F1RMR5CT7GKWBHXN921&pf_rd_p=843e77b6-8834-4ef1-bf3b-ecc146b1b1bb",
    "https://www.amazon.in/tez/browse/explore/collection?qcbrand=qqfsWw9RkO&nodeId=204870002031&title=Atta+Dal+%26+More&pf_rd_r=7F1RMR5CT7GKWBHXN921&pf_rd_p=843e77b6-8834-4ef1-bf3b-ecc146b1b1bb",
    "https://www.amazon.in/tez/browse/explore/collection?qcbrand=qqfsWw9RkO&nodeId=218876203031&title=Chicken%2C+Meat+%26+Fish&pf_rd_r=7F1RMR5CT7GKWBHXN921&pf_rd_p=843e77b6-8834-4ef1-bf3b-ecc146b1b1bb",
    "https://www.amazon.in/tez/browse/explore/collection?qcbrand=qqfsWw9RkO&nodeId=206264743031&title=Kitchen+Essentials&pf_rd_r=7F1RMR5CT7GKWBHXN921&pf_rd_p=843e77b6-8834-4ef1-bf3b-ecc146b1b1bb",
    "https://www.amazon.in/tez/browse/explore/collection?qcbrand=qqfsWw9RkO&nodeId=205015906031&title=Oral+Care&pf_rd_r=7F1RMR5CT7GKWBHXN921&pf_rd_p=843e77b6-8834-4ef1-bf3b-ecc146b1b1bb",
    "https://www.amazon.in/tez/browse/explore/collection?qcbrand=qqfsWw9RkO&nodeId=205015909031&title=Sexual+Wellness&pf_rd_r=7F1RMR5CT7GKWBHXN921&pf_rd_p=843e77b6-8834-4ef1-bf3b-ecc146b1b1bb"
]

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

def send_status_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

async def scan_amazon_now():
    price_database = load_json(DATA_FILE, {})
    updated_database = {}
    cookies = load_json(COOKIES_FILE, [])
    
    total_items_scanned = 0
    error_log = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        if cookies:
            valid_cookies = [{k: v for k, v in c.items() if k in ['name', 'value', 'domain', 'path']} for c in cookies]
            await context.add_cookies(valid_cookies)

        page = await context.new_page()

        for url in AMAZON_NOW_URLS:
            try:
                category_name = url.split('title=')[1].split('&')[0] if 'title=' in url else 'Category'
                
                await page.goto(url, wait_until="networkidle")
                
                if await page.query_selector('form[action="/errors/validateCaptcha"]'):
                    error_log.append(f"🤖 Captcha blocked: {category_name}")
                    continue

                products = await page.query_selector_all('div[data-asin]')
                
                if len(products) == 0:
                    try:
                        page_title = await page.title()
                        print(f"\n--- DEBUG INFO FOR {category_name} ---")
                        print(f"Page Title: {page_title}")
                        
                        page_text = await page.inner_text('body')
                        print(f"Page Content Snippet: {page_text[:200]}...") 
                        print("--------------------------------------\n")
                        
                        error_log.append(f"⚠️ 0 items ({page_title[:15]}...)")
                    except Exception as e:
                        print(f"Failed to get debug info: {e}")
                        error_log.append(f"⚠️ 0 items (Error loading page title)")
                    continue

                for product in products:
                    try:
                        asin = await product.get_attribute('data-asin')
                        if not asin: continue

                        title_element = await product.query_selector('h2 a span') or await product.query_selector('span.a-text-normal')
                        price_element = await product.query_selector('.a-price .a-offscreen')
                        link_element = await product.query_selector('h2 a') or await product.query_selector('a.a-link-normal')

                        if title_element and price_element and link_element:
                            title = await title_element.inner_text()
                            raw_price = await price_element.inner_text()
                            new_price = float(raw_price.replace('₹', '').replace(',', '').strip())
                            link = "https://www.amazon.in" + await link_element.get_attribute('href')

                            if asin in price_database:
                                old_price = price_database[asin]['price']
                                if new_price < old_price:
                                    send_telegram_alert(title, new_price, old_price, link)
                            
                            updated_database[asin] = {"title": title, "price": new_price, "link": link}
                            total_items_scanned += 1
                    except Exception:
                        continue
                
                await asyncio.sleep(3) 

            except Exception as e:
                error_log.append(f"❌ Error loading {category_name}: {str(e)[:40]}")
                continue

        await browser.close()
    
    price_database.update(updated_database)
    save_json(DATA_FILE, price_database)
    
    if total_items_scanned > 0:
        status_msg = f"✅ *Amazon Now Scan Complete*\n📦 Scanned: `{total_items_scanned}` products."
    else:
        status_msg = f"❌ *Amazon Now Scan FAILED*\n📦 Scanned: `{total_items_scanned}` products."
        
    if error_log:
        status_msg += "\n\n*⚠️ Warning/Errors:*\n"
        for err in set(error_log):
            status_msg += f"- {err}\n"
            
    send_status_message(status_msg)

if __name__ == "__main__":
    asyncio.run(scan_amazon_now())
