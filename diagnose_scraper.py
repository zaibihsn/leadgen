import asyncio
import pandas as pd
import sys
import os
import json
from scraper import scrape_google_maps

async def run_diagnostics():
    query = "Restaurant in Gujranwala"
    strategy = "Fastest"
    website_filter = "No Website"
    phone_filter = "Has Phone"
    
    print(f"[SEARCH] Running Diagnostics for: '{query}'")
    print(f"[PARAMS] Strategy: {strategy} | Website: {website_filter} | Phone: {phone_filter}")
    print("-" * 50)
    
    # We bypass the standard call to see internal steps
    import scraper
    
    # 1. Run Engine
    print(f"Step 1: Running Go Engine...")
    df_raw = await scrape_google_maps([query], strategy=strategy, website_required="Either", phone_required="Either")
    
    if df_raw.empty:
        print("FAILED: Engine returned 0 results even WITHOUT filters.")
        return

    print(f"SUCCESS: Engine returned {len(df_raw)} raw results.")
    print(f"Raw Columns: {list(df_raw.columns)}")
    
    # 2. Check Website Mapping
    print("\nStep 2: Checking Website/Phone data...")
    # These are already mapped in scrape_google_maps if we use it
    has_web = len(df_raw[df_raw['Website'].astype(str).str.contains('http', na=False)])
    has_phone = len(df_raw[df_raw['Phone'].astype(str).str.len() > 5])
    
    print(f"Leads with Website: {has_web}/{len(df_raw)}")
    print(f"Leads with Phone: {has_phone}/{len(df_raw)}")
    
    # 3. Simulate User's Filter ("No Website")
    print("\nStep 3: Applying 'No Website' Filter...")
    df_no_web = df_raw[~df_raw['Website'].astype(str).str.contains('http', na=False)]
    print(f"Remaining after 'No Website': {len(df_no_web)}")
    if not df_no_web.empty:
        print("Sample Lead Websites (should be empty/none):")
        print(df_no_web['Website'].head().tolist())

    # 4. Simulate User's Filter ("Has Phone")
    print("\nStep 4: Applying 'Has Phone' Filter...")
    df_final = df_no_web[df_no_web['Phone'].astype(str).str.len() > 5]
    print(f"Remaining after 'Has Phone': {len(df_final)}")
    
    if df_final.empty:
        print("\nRESULT: Zero results reached due to filtering.")
        if len(df_raw) > 0 and len(df_final) == 0:
            print("Reason: Every result found had a website OR lacked a phone number.")

if __name__ == "__main__":
    asyncio.run(run_diagnostics())
