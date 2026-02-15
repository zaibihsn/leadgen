import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def scrape_google_maps(cities, query_type="manufacturers", max_results=50):
    """
    Scrapes Google Maps for businesses in specific cities that do NOT have a website.
    """
    all_results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()

        for city in cities:
            search_query = f"{query_type} in {city}"
            logger.info(f"Searching for: {search_query}")
            
            await page.goto(f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}")
            
            # Wait for results to load
            try:
                await page.wait_for_selector('div[role="feed"]', timeout=10000)
            except:
                logger.warning(f"No feed found for {city}. Might be zero results or different layout.")
                continue

            # Scrolling logic to load more results
            last_height = 0
            results_found = 0
            
            while results_found < max_results:
                # Scroll the feed
                await page.mouse.move(500, 500) # Move to the results area
                await page.mouse.wheel(0, 2000)
                await asyncio.sleep(2)
                
                # Check for "You've reached the end of the list" or similar
                # For now, we just count results found
                listings = await page.query_selector_all('div[role="article"]')
                if len(listings) == results_found:
                    break # No more results loading
                results_found = len(listings)
                logger.info(f"Loading results... {results_found} found so far.")

            # Extract data from loaded listings
            listings = await page.query_selector_all('div[role="article"]')
            for listing in listings:
                try:
                    # Click listing to see details (sometimes needed for website info)
                    # For performance, we first try to find website from the list view
                    
                    name_el = await listing.query_selector('div.fontHeadlineSmall')
                    name = await name_el.inner_text() if name_el else "Unknown"
                    
                    rating_el = await listing.query_selector('span.MW4etd')
                    rating = await rating_el.inner_text() if rating_el else "0"
                    
                    reviews_el = await listing.query_selector('span.Uy7F9')
                    reviews = await reviews_el.inner_text() if reviews_el else "0"
                    reviews = reviews.replace('(', '').replace(')', '').replace(',', '')
                    
                    # Look for website link in the article
                    website_el = await listing.query_selector('a[aria-label*="website"]')
                    website = await website_el.get_attribute('href') if website_el else None
                    
                    if not website:
                        all_results.append({
                            'Company Name': name,
                            'Stars': float(rating) if rating != "Unknown" else 0.0,
                            'Reviews': int(reviews) if reviews.isdigit() else 0,
                            'City': city,
                            'Website': 'None'
                        })
                except Exception as e:
                    logger.error(f"Error processing a listing: {e}")

        await browser.close()
    
    # Sort results
    df = pd.DataFrame(all_results)
    if not df.empty:
        df = df.sort_values(by=['Stars', 'Reviews'], ascending=False)
    
    return df

if __name__ == "__main__":
    # Test run
    test_cities = ["Trenton"]
    results = asyncio.run(scrape_google_maps(test_cities, max_results=10))
    print(results)
