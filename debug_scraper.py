import asyncio
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)

async def debug_scrape(city="Gujranwala"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        search_query = f"manufacturers in {city}"
        url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
        print(f"Navigating to {url}")
        
        try:
            await page.goto(url)
            await asyncio.sleep(5) # Give it time to load
            
            # Check for consent popup
            consent_btn = await page.query_selector('button[aria-label="Accept all"]')
            if consent_btn:
                print("Clicking consent button...")
                await consent_btn.click()
                await asyncio.sleep(2)

            # Take screenshot to see current state
            await page.screenshot(path="debug_maps.png")
            print("Screenshot saved to debug_maps.png")
            
            # Check if feed exists
            feed = await page.query_selector('div[role="feed"]')
            if feed:
                print("Feed found!")
            else:
                print("Feed NOT found.")
                # Print page title
                print(f"Page title: {await page.title()}")
                
        except Exception as e:
            print(f"Debug failed: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_scrape())
