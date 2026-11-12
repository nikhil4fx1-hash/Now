import asyncio
import os
import requests
from playwright.async_api import async_playwright

BLINKIT_URL = "https://blinkit.com/dc/?collection_uuid=OTg3NjU0MzIxMjM0NTMzNzE%3D&is_plp=true"
TELEGRAM_BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.environ.get('CHANNEL_ID')

def send_photo_to_telegram(photo_path, caption):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        print("Telegram credentials missing!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    with open(photo_path, 'rb') as photo:
        payload = {"chat_id": TELEGRAM_CHANNEL_ID, "caption": caption}
        files = {"photo": photo}
        response = requests.post(url, data=payload, files=files)
        if response.status_code == 200:
            print("Screenshot sent to Telegram successfully!")
        else:
            print(f"Failed to send screenshot: {response.text}")

async def test_blinkit():
    print("Starting Blinkit Test...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # ലൊക്കേഷൻ ഇന്ത്യയിലാണെന്ന് കാണിക്കാൻ മുംബൈയിലെ കോർഡിനേറ്റ്സ് കൊടുക്കുന്നു
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            geolocation={"longitude": 72.8777, "latitude": 19.0760}, 
            permissions=["geolocation"]
        )
        page = await context.new_page()
        
        try:
            print(f"Loading URL: {BLINKIT_URL}")
            await page.goto(BLINKIT_URL, wait_until="domcontentloaded", timeout=40000)
            
            # പേജ് പൂർണ്ണമായി ലോഡ് ആകാൻ 8 സെക്കൻഡ് കാത്തിരിക്കുന്നു
            await asyncio.sleep(8)
            
            title = await page.title()
            print(f"\n✅ Page Title: {title}")
            
            # സ്ക്രീൻഷോട്ട് എടുക്കുന്നു
            screenshot_path = "blinkit_debug.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print("✅ Screenshot saved.")
            
            # സ്ക്രീൻഷോട്ട് ടെലിഗ്രാമിലേക്ക് അയക്കുന്നു
            send_photo_to_telegram(screenshot_path, "Blinkit Debug Screenshot")
            
            # പേജിൽ എവിടെയെങ്കിലും വില (₹) കാണിക്കുന്നുണ്ടോ എന്ന് സെർച്ച് ചെയ്യുന്നു
            js_script = """
            () => {
                let items = [];
                let elements = document.querySelectorAll('div, a');
                elements.forEach(el => {
                    if(el.innerText && el.innerText.includes('₹') && el.innerText.length < 150) {
                        items.push(el.innerText.replace(/\\n/g, ' | '));
                    }
                });
                return [...new Set(items)].slice(0, 15);
            }
            """
            extracted_data = await page.evaluate(js_script)
            
            print("\n--- Extracted Data (₹) ---")
            if extracted_data:
                for item in extracted_data:
                    print(item)
            else:
                print("No products or prices found. Probably asking for location!")
            print("--------------------------\n")
            
        except Exception as e:
            print(f"❌ Error occurred: {e}")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_blinkit())
