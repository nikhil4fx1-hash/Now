
import asyncio
import os
import requests
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

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
    print("Starting Stealth Blinkit Test...")
    async with async_playwright() as p:
        # ബോട്ട് ആണെന്ന് മനസ്സിലാകാതിരിക്കാൻ പ്രത്യേക ആർഗ്യുമെന്റ്സ് നൽകുന്നു
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            geolocation={"longitude": 72.8777, "latitude": 19.0760}, 
            permissions=["geolocation"],
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        # Stealth മോഡ് ആക്റ്റീവ് ആക്കുന്നു
        await stealth_async(page)
        
        try:
            print(f"Loading URL: {BLINKIT_URL}")
            await page.goto(BLINKIT_URL, wait_until="domcontentloaded", timeout=45000)
            
            await asyncio.sleep(10)
            
            title = await page.title()
            print(f"\n✅ Page Title: {title}")
            
            screenshot_path = "blinkit_debug.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print("✅ Screenshot saved.")
            
            send_photo_to_telegram(screenshot_path, "Blinkit Stealth Debug Screenshot")
            
        except Exception as e:
            print(f"❌ Error occurred: {e}")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_blinkit())
