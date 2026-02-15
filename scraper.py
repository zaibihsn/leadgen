import asyncio
import pandas as pd
import logging
import sys
import os
import subprocess
import json
import tempfile
import uuid
import platform
import urllib.request

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def scrape_google_maps(queries, strategy="Fast (Default)", max_results=50, website_required="Either", phone_required="Either"):
    """
    Subprocess wrapper for gosom/google-maps-scraper Go binary.
    Auto-detects OS and downloads Linux binary if running on Streamlit Cloud.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    is_linux = platform.system().lower() == "linux"
    
    # Use 'rod' version on Linux as it's more stable in cloud environments
    binary_name = "gmaps_scraper_rod" if is_linux else "gmaps_scraper.exe"
    binary_path = os.path.join(base_dir, "gosom_scraper", binary_name)
    
    # Auto-download for Linux (Streamlit Cloud)
    if is_linux and not os.path.exists(binary_path):
        logger.info("🐧 Linux detected and binary missing. Downloading Nitro Engine (Rod)...")
        try:
            os.makedirs(os.path.dirname(binary_path), exist_ok=True)
            # Use the ROD version for better cloud compatibility
            asset_name = "google_maps_scraper-1.10.1-rod-linux-amd64"
            url = f"https://github.com/gosom/google-maps-scraper/releases/download/v1.10.1/{asset_name}"
            urllib.request.urlretrieve(url, binary_path)
            
            # Set executable permissions
            os.chmod(binary_path, 0o755)
            logger.info("✅ Nitro Engine (Rod) installed successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to download Nitro Engine: {e}")
            return pd.DataFrame()

    if not os.path.exists(binary_path):
        logger.error(f"❌ Critical Error: Nitro Engine not found at {binary_path}")
        return pd.DataFrame()

    # Strategy Mapping
    depth = 10
    fast_mode = False
    zoom = 15
    
    if strategy == "Fastest":
        depth = 1
    elif strategy == "Detailed":
        depth = 30
    elif "Zoom" in strategy:
        try:
            zoom = int(strategy.split(" ")[1])
            depth = 15
        except: pass

    # Prepare local temp directory
    tmp_dir = os.path.join(base_dir, ".tmp")
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir, exist_ok=True)

    # Prepare input file
    run_id = str(uuid.uuid4())[:8]
    input_file_path = os.path.join(tmp_dir, f"gmaps_q_{run_id}.txt")
    with open(input_file_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(queries))

    # Prepare output file
    output_file_path = os.path.join(tmp_dir, f"gmaps_r_{run_id}.json")
    if os.path.exists(output_file_path): os.remove(output_file_path)
    
    # CLI Command Construction
    concurrency = "1" if is_linux else "4"
    
    cmd = [
        binary_path,
        "-input", input_file_path,
        "-results", output_file_path,
        "-json",
        "-depth", str(depth),
        "-c", concurrency,
        "-exit-on-inactivity", "2m"
    ]
    
    if "Zoom" in strategy:
        cmd.extend(["-zoom", str(zoom)])

    logger.info(f"🚀 Launching Go Engine: {' '.join(cmd)}")
    
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            err_msg = stderr.decode()[:1000]
            logger.error(f"❌ Go Engine failed: {err_msg}")
            return pd.DataFrame()

        # Load results
        if os.path.exists(output_file_path):
            results = []
            with open(output_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            results.append(json.loads(line))
                        except: pass
            
            df = pd.DataFrame(results)
            if df.empty: return df

            # Field Mapping
            mapping = {
                'title': 'Business Name',
                'review_rating': 'Stars',
                'review_count': 'Reviews',
                'phone': 'Phone',
                'web_site': 'Website',
                'category': 'Category',
                'address': 'Address'
            }
            cols = {k: v for k, v in mapping.items() if k in df.columns}
            df = df.rename(columns=cols)
            
            # Standardization
            for col in ['Website', 'Phone']:
                if col not in df.columns: df[col] = ""
            df['Website'] = df['Website'].fillna("")
            df['Phone'] = df['Phone'].fillna("")

            # Filtering
            pre_filter = len(df)
            if website_required == "Has Website":
                df = df[df['Website'].astype(str).str.contains('http', na=False)]
            elif website_required == "No Website":
                df = df[~df['Website'].astype(str).str.contains('http', na=False)]
                
            if phone_required == "Has Phone":
                df = df[df['Phone'].astype(str).str.len() > 5]
            elif phone_required == "No Phone":
                df = df[df['Phone'].astype(str).str.len() <= 5]

            if max_results and len(df) > max_results:
                df = df.head(max_results)

            logger.info(f"🎯 Final results: {len(df)} (Filtered: {pre_filter - len(df)})")
            return df
        
    except Exception as e:
        logger.error(f"❌ Subprocess Exception: {e}")
    finally:
        try:
            if os.path.exists(input_file_path): os.remove(input_file_path)
            if os.path.exists(output_file_path): os.remove(output_file_path)
        except: pass

    return pd.DataFrame()
