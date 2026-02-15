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
import tarfile

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
    
    binary_name = "gmaps_scraper" if is_linux else "gmaps_scraper.exe"
    binary_path = os.path.join(base_dir, "gosom_scraper", binary_name)
    
    # Auto-download for Linux (Streamlit Cloud)
    if is_linux and not os.path.exists(binary_path):
        logger.info("🐧 Linux detected and binary missing. Downloading Nitro Engine...")
        try:
            os.makedirs(os.path.dirname(binary_path), exist_ok=True)
            url = "https://github.com/gosom/google-maps-scraper/releases/download/v1.10.1/google_maps_scraper-1.10.1-linux-amd64.tar.gz"
            tar_path = os.path.join(base_dir, "gosom_scraper", "engine.tar.gz")
            urllib.request.urlretrieve(url, tar_path)
            
            with tarfile.open(tar_path, "r:gz") as tar:
                # The binary inside is named 'google_maps_scraper'
                tar.extractall(path=os.path.join(base_dir, "gosom_scraper"))
            
            # Find the extracted file (it might have a different name)
            extracted_path = os.path.join(base_dir, "gosom_scraper", "google_maps_scraper")
            if os.path.exists(extracted_path):
                os.rename(extracted_path, binary_path)
                os.chmod(binary_path, 0o755)
                logger.info("✅ Nitro Engine installed successfully.")
            
            os.remove(tar_path)
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
        fast_mode = False # Keep False unless we have geo coordinates
    elif strategy == "Detailed":
        depth = 30
    elif "Zoom" in strategy:
        try:
            zoom = int(strategy.split(" ")[1])
            depth = 15
        except: pass

    # Prepare local temp directory to avoid permission issues
    tmp_dir = os.path.join(base_dir, ".tmp")
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir, exist_ok=True)

    # Prepare input file (Unique per call)
    run_id = str(uuid.uuid4())[:8]
    input_file_path = os.path.join(tmp_dir, f"gmaps_q_{run_id}.txt")
    with open(input_file_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(queries))

    # Prepare output file
    output_file_path = os.path.join(tmp_dir, f"gmaps_r_{run_id}.json")
    if os.path.exists(output_file_path): os.remove(output_file_path)
    
    # CLI Command Construction
    cmd = [
        binary_path,
        "-input", input_file_path,
        "-results", output_file_path,
        "-json",
        "-depth", str(depth),
        "-c", "4",
        "-exit-on-inactivity", "2m"
    ]
    
    if fast_mode:
        cmd.append("-fast-mode")
    if "Zoom" in strategy:
        cmd.extend(["-zoom", str(zoom)])

    logger.info(f"🚀 Launching Go Engine: {' '.join(cmd)}")
    logger.info(f"📍 Params -> Depth: {depth}, Strategy: {strategy}, Input: {input_file_path}")
    
    try:
        # Run the binary as async subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            err_msg = stderr.decode()[:1000]
            logger.error(f"❌ Go Engine failed (Code {process.returncode}): {err_msg}")
            return pd.DataFrame()

        # Load results
        if os.path.exists(output_file_path):
            results = []
            try:
                # Try reading line-separated JSON first (standard for this scraper)
                with open(output_file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                results.append(json.loads(line))
                            except: pass
                
                # If nothing found, try reading as a single JSON array
                if not results:
                    with open(output_file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            try:
                                results = json.loads(content)
                            except: pass
            except Exception as e:
                logger.error(f"❌ Parsing Error: {e}")
            
            if not isinstance(results, list):
                results = [results] if results else []

            logger.info(f"📈 Raw results captured: {len(results)}")
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
            logger.info(f"🧪 Applying Filters -> Web: {website_required}, Phone: {phone_required}")
            
            if website_required == "Has Website":
                df = df[df['Website'].astype(str).str.contains('http', na=False)]
            elif website_required == "No Website":
                df = df[~df['Website'].astype(str).str.contains('http', na=False)]
                
            if phone_required == "Has Phone":
                df = df[df['Phone'].astype(str).str.len() > 5]
            elif phone_required == "No Phone":
                df = df[df['Phone'].astype(str).str.len() <= 5]

            # Capping results
            if max_results and len(df) > max_results:
                df = df.head(max_results)

            logger.info(f"🎯 Final Dataframe Size: {len(df)} (Filtered: {pre_filter - len(df)})")
            return df
        
    except Exception as e:
        logger.error(f"❌ Subprocess Exception: {e}")
    finally:
        # Cleanup
        try:
            if os.path.exists(input_file_path): os.remove(input_file_path)
            if os.path.exists(output_file_path): os.remove(output_file_path)
        except: pass

    return pd.DataFrame()

if __name__ == "__main__":
    # Internal test
    async def test():
        df = await scrape_google_maps(["Restaurant in Gujranwala"], strategy="Fastest")
        print(df.head())
    asyncio.run(test())
