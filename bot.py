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
                
                # കൂടുതൽ പ്രൊഡക്റ്റുകൾ ലോഡ് ചെയ്യാൻ വേണ്ടി പേജ് അല്പം താഴേക്ക് സ്ക്രോൾ ചെയ്യുന്നു
                await page.evaluate("window.scrollBy(0, 1000);")
                await asyncio.sleep(2)

                # ആമസോൺ ഘടന മാറ്റിയാലും ടെക്സ്റ്റിൽ നിന്നും വിലയും പേരും എടുക്കാനുള്ള Smart JS Parser
                js_script = """
                () => {
                    let results = {};
                    let elements = Array.from(document.querySelectorAll('span, div, p'))
                        .filter(el => el.children.length === 0 && el.innerText && el.innerText.includes('₹'));
                    
                    let processedCards = new Set();

                    elements.forEach(el => {
                        let card = el;
                        let attempts = 0;
                        while(card.parentElement && attempts < 10) {
                            let parent = card.parentElement;
                            if(parent.querySelectorAll('img').length > 1 || parent.innerText.length > 350) {
                                break; 
                            }
                            card = parent;
                            attempts++;
                        }

                        if(processedCards.has(card)) return;
                        processedCards.add(card);

                        let text = card.innerText;
                        if(!text || text.length > 350) return;

                        let lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                        
                        let priceMatch = text.match(/₹\\s*([0-9,]+(?:\\.[0-9]+)?)/);
                        if(!priceMatch) return;
                        let price = parseFloat(priceMatch[1].replace(/,/g, ''));
                        
                        let title = "";
                        let titleIndex = -1;
                        for(let i=0; i<lines.length; i++) {
                            let lower = lines[i].toLowerCase();
                            if(lower.includes('★') || lower.includes('mins') || lines[i].match(/^[0-9.]+$/) || lower.includes('%') || lower.includes('₹') || lower === 'add' || lower === 'sponsored' || lower.includes('shop by') || lower.includes('delivery')) {
                                continue;
                            }
                            if(lines[i].length > 7) {
                                title = lines[i];
                                titleIndex = i;
                                break;
                            }
                        }
                        
                        if (title) {
                            // പ്രൊഡക്റ്റിന്റെ ഭാരം കൂടി പേരിനൊപ്പം ചേർക്കുന്നു (ഉദാഹരണത്തിന്: 500 g, 1 L)
                            if(titleIndex !== -1 && titleIndex + 1 < lines.length) {
                                let nextLine = lines[titleIndex + 1];
                                if(nextLine.length > 1 && nextLine.length < 15 && !nextLine.includes('₹') && !nextLine.includes('%')) {
                                    title = title + " (" + nextLine + ")";
                                }
                            }
                            
                            let uid = title.toLowerCase().replace(/[^a-z0-9]/g, '');
                            if(uid.length > 5) {
                                let linkEl = card.querySelector('a');
                                let link = linkEl ? linkEl.href : window.location.href;
                                results[uid] = {
                                    title: title,
                                    price: price,
                                    link: link
                                };
                            }
                        }
                    });
                    return results;
                }
                """
                extracted_products = await page.evaluate(js_script)
                
                if len(extracted_products) == 0:
                    try:
                        page_title = await page.title()
                        error_log.append(f"⚠️ 0 items ({page_title[:15]}...)")
                    except:
                        pass
                    continue

                for uid, data in extracted_products.items():
                    title = data['title']
                    new_price = data['price']
                    link = data['link']

                    if uid in price_database:
                        old_price = price_database[uid]['price']
                        if new_price < old_price:
                            send_telegram_alert(title, new_price, old_price, link)
                    
                    updated_database[uid] = {"title": title, "price": new_price, "link": link}
                    total_items_scanned += 1
                
                await asyncio.sleep(2) 

            except Exception as e:
                error_log.append(f"❌ Error loading {category_name}: {str(e)[:40]}")
                continue

        await browser.close()
    
    price_database.update(updated_database)
    save_json(DATA_FILE, price_database)
    
    if total_items_scanned > 0:
        status_msg = f"✅ *Amazon Now Scan Complete*\n📦 Scanned: `{total_items_scanned}` products successfully."
    else:
        status_msg = f"❌ *Amazon Now Scan FAILED*\n📦 Scanned: `{total_items_scanned}` products."
        
    if error_log:
        status_msg += "\n\n*⚠️ Warning/Errors:*\n"
        for err in set(error_log):
            status_msg += f"- {err}\n"
            
    send_status_message(status_msg)

if __name__ == "__main__":
    asyncio.run(scan_amazon_now())
