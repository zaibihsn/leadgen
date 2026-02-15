import streamlit as st
import asyncio
import pandas as pd
from scraper import scrape_google_maps
from locations import LOCATIONS, CATEGORIES
import base64
from io import BytesIO
import sys
import nest_asyncio
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Windows-specific fix for Playwright/Asyncio subprocesses
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

nest_asyncio.apply()

# Page config
st.set_page_config(page_title="LeadGen Pro | High-Performance Scraper", page_icon="🚀", layout="wide")

# Enhanced CSS for premium "Clean & Minimalist" Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@300;400;600;800&display=swap');

    :root {
        --primary: #3b82f6;
        --bg-main: #0f172a;
        --bg-sidebar: #020617;
        --card-bg: #1e293b;
        --text-main: #f8fafc;
        --text-muted: #94a3b8;
        --border: rgba(255, 255, 255, 0.05);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background-color: var(--bg-main);
        color: var(--text-main);
    }

    .stApp {
        background: transparent;
    }

    /* Minimalist Sidebar */
    [data-testid="stSidebar"] {
        background: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border);
    }

    /* Clean Cards */
    .stMetric, .stDataFrame, .stAlert, div.stBlock, .element-container {
        border-radius: 16px !important;
        border: 1px solid var(--border) !important;
        background: var(--card-bg) !important;
        padding: 24px !important;
    }

    /* Minimalist Header */
    .main-title {
        font-family: 'Outfit', sans-serif;
        color: var(--text-main);
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0px;
        letter-spacing: -0.05em;
    }

    .sub-title {
        color: var(--text-muted);
        text-align: center;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 4rem;
    }

    /* Clean Buttons */
    .stButton>button {
        width: 100%;
        background-color: var(--primary);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }

    .stButton>button:active {
        transform: translateY(0px);
    }

    /* Sidebar Content */
    .sidebar-header {
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 2rem;
    }

    /* Dataframe Tuning */
    .stDataFrame {
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

def get_csv_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="leads_export.csv" style="text-decoration: none;"><button style="width: 100%; background-color: transparent; color: #10b981; border: 1px solid #10b981; padding: 12px; border-radius: 12px; cursor: pointer; font-weight: 600; margin-top: 15px;">Export Data (CSV)</button></a>'
    return href

def main():
    # --- Title Section ---

    col_title_1, col_title_2, col_title_3 = st.columns([1, 2, 1])
    with col_title_2:
        st.markdown("""
        <div align="center" style="margin-top: 0;">
          <h1 style="font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 3rem;">✨ Google Maps Scraper 🤖</h1>
        </div>
        <p align="center">
          <a href="#"><img alt="google-maps-scraper forks" src="https://img.shields.io/github/forks/omkarcloud/google-maps-scraper?style=for-the-badge" /></a>
          <a href="#"><img alt="Repo stars" src="https://img.shields.io/github/stars/omkarcloud/google-maps-scraper?style=for-the-badge&color=yellow" /></a>
          <a href="#"><img alt="issues" src="https://img.shields.io/github/issues/omkarcloud/google-maps-scraper?color=purple&style=for-the-badge" /></a>
        </p>
        <p align="center">
          <img src="https://views.whatilearened.today/views/github/omkarcloud/google-maps-scraper.svg" width="80px" height="28px" alt="View" />
        </p>
        <div style="margin-bottom: 40px;"></div>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### 🛠️ Nitro Engine")
        if st.button("🔍 Run Health Check"):
            try:
                import subprocess
                base_dir = os.path.dirname(os.path.abspath(__file__))
                binary_path = os.path.join(base_dir, "gosom_scraper", "gmaps_scraper.exe")
                if os.path.exists(binary_path):
                    st.info(f"Checking: {binary_path}")
                    res = subprocess.run([binary_path, "--help"], capture_output=True, text=True, timeout=5)
                    if res.returncode == 0:
                        st.success("✅ Engine is REACHABLE!")
                    else:
                        st.error(f"❌ Engine Error: {res.stderr[:200]}")
                else:
                    st.error(f"❌ Binary NOT FOUND at {binary_path}")
            except Exception as e:
                st.error(f"❌ Check Failed: {e}")
        
        st.divider()
        st.markdown("**System Paths:**")
        st.code(f"CWD: {os.getcwd()}\nFile: {__file__}")

    # --- Dashboard Tabs ---
    tab_home, tab_output, tab_results = st.tabs(["🏠 Home", "📊 Output Manager", "💎 Data Warehouse"])

    with tab_home:
        # Sidebar-style settings inside Home tab or using columns
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.markdown("### 🏷️ Search Queries")
            query_mode = st.radio("Input Type", ["List of Queries", "List of Links", "Industry x Country", "Reviews Scraper"], horizontal=True)
            
            if query_mode == "List of Queries":
                st.markdown("💡 **Quick Suggestions:**")
                # Define examples
                examples = ["Restaurant in Gujranwala", "Dentist in London", "Software Companies in New York", "Gyms in Dubai"]
                
                # Show as horizontal tags (columns)
                cols_ex = st.columns(len(examples))
                for idx, ex in enumerate(examples):
                    if cols_ex[idx].button(f"➕ {ex.split(' in ')[0]}", key=f"ex_{idx}", help=f"Add '{ex}'"):
                        if 'current_queries' not in st.session_state:
                            st.session_state['current_queries'] = ""
                        
                        existing = st.session_state['current_queries'].strip()
                        if ex not in existing:
                            st.session_state['current_queries'] = (existing + "\n" + ex).strip()

                queries = st.text_area(
                    "Enter search terms (one per line)", 
                    value=st.session_state.get('current_queries', ""),
                    placeholder="e.g. Restaurants in New York\nWeb Developers in London", 
                    height=150,
                    key="current_queries"
                )
            elif query_mode == "List of Links":
                links = st.text_area("Enter Google Maps links (one per line)", placeholder="https://www.google.com/maps/search/...", height=150)
            elif query_mode == "Industry x Country":
                target_country = st.selectbox("Select Country", ["-- Browse All --"] + list(LOCATIONS.keys()))
                industry = st.selectbox("Business Type", ["--- ALL CATEGORIES ---"] + CATEGORIES)
            elif query_mode == "Reviews Scraper":
                review_links = st.text_area("Enter business links to scrape reviews for", height=150)

        with c2:
            st.markdown("### 🏎️ Search Strategy")
            strategy = st.select_slider(
                "Select Extraction Intensity",
                options=["Fastest", "Fast (Default)", "Detailed", "Zoom 15", "Zoom 16", "Zoom 17", "Zoom 18", "Geolocation"],
                value="Fast (Default)"
            )
            
            st.markdown("### 🔍 Lead Quality Filters")
            web_filter = st.selectbox("Website Status", ["Either", "No Website", "Has Website"], index=0)
            phone_filter = st.selectbox("Phone Status", ["Either", "Has Phone", "No Phone"], index=0)
            
            max_results = st.number_input("Max Results Per search", 5, 5000, 50)

        st.divider()
        
        # Geolocation configuration if selected
        if strategy == "Geolocation":
            st.info("🌐 Geolocation Mode Enabled: Paste your GeoJSON polygons below.")
            polygon_data = st.text_area("GeoJSON Polygons Data", height=100)

        if strategy == "Geolocation":
            st.info("🌐 Geolocation Mode Enabled: Paste your GeoJSON polygons below.")
            polygon_data = st.text_area("GeoJSON Polygons Data", height=100)

        # Consolidate Inputs for Home tab
        final_queries = []
        if query_mode == "List of Queries":
            final_queries = [q.strip() for q in queries.split('\n') if q.strip()]
        elif query_mode == "List of Links":
            final_queries = [l.strip() for l in links.split('\n') if l.strip()]
        elif query_mode == "Industry x Country":
            if target_country != "-- Browse All --":
                final_queries = [f"{industry} in {loc}" for loc in LOCATIONS[target_country]]
        elif query_mode == "Reviews Scraper":
            final_queries = [l.strip() for l in review_links.split('\n') if l.strip()]

        if st.button("🚀 INITIATE GLOBAL EXTRACTION"):
            if not final_queries:
                st.warning("⚠️ Critical data missing: Please provide search queries or locations.")
            else:
                status_container = st.empty()
                progress_bar = st.progress(0.0)
                
                async def run_overhaul_scrape():
                    # Limit concurrency for parallel bots
                    sem = asyncio.Semaphore(3)
                    
                    async def worker(q):
                        async with sem:
                            try:
                                return await scrape_google_maps(
                                    [q], 
                                    strategy=strategy,
                                    max_results=max_results,
                                    website_required=web_filter,
                                    phone_required=phone_filter
                                )
                            except Exception as e:
                                logger.error(f"Worker error for {q}: {e}")
                                return pd.DataFrame()

                    all_results = []
                    total = len(final_queries)
                    
                    # Process in chunks or parallel
                    tasks = [worker(q) for q in final_queries]
                    
                    # Update progress as tasks complete
                    results = []
                    for i, future in enumerate(asyncio.as_completed(tasks)):
                        try:
                            df_batch = await future
                            if not df_batch.empty:
                                results.append(df_batch)
                            progress_bar.progress((i + 1) / total)
                            status_container.info(f"⏳ Processed {i+1}/{total} bots. Found {len(df_batch) if not df_batch.empty else 0} leads in last stream.")
                        except Exception as e:
                            st.error(f"❌ Thread Error: {e}")
                    
                    if results:
                        final_df = pd.concat(results)
                        # Go data contains lists (emails, reviews) which are unhashable. 
                        # We drop duplicates based on the Google Maps URL which is unique and string-based.
                        if 'link' in final_df.columns:
                            final_df = final_df.drop_duplicates(subset=['link'])
                        else:
                            final_df = final_df.drop_duplicates(subset=['Business Name', 'Address'], keep='first')
                        
                        st.session_state['last_results'] = final_df
                        return final_df
                    else:
                        st.error("⚠️ The engine finished but returned 0 results. This usually means the search terms were too specific or filters were too strict.")
                    return pd.DataFrame()

                with st.spinner("🤖 Multi-threaded bots are extracting data in parallel..."):
                    asyncio.run(run_overhaul_scrape())
                st.success("💎 Extraction Complete! Switch to 'Data Warehouse' to view results.")

    with tab_output:
        st.markdown("### 📊 Active Extraction Streams")
        if 'last_results' in st.session_state:
            st.info(f"✅ Last task completed with {len(st.session_state['last_results'])} results.")
        else:
            st.write("No active or recent tasks found. Start a task from the **Home** tab.")
        
        st.divider()
        st.markdown("### 🔍 Nitro Engine Diagnostics")
        if st.button("🧪 Run Live Engine Test"):
            with st.status("🛠️ Running Diagnostic (Restaurant in Gujranwala)..."):
                try:
                    # Run without filters first
                    df_raw = asyncio.run(scrape_google_maps(["Restaurant in Gujranwala"], strategy="Fastest", website_required="Either", phone_required="Either"))
                    
                    st.write(f"**Step 1: Raw Engine Check**")
                    if df_raw.empty:
                        st.error("❌ Engine returned 0 results. It might be blocked or failing to launch.")
                    else:
                        st.success(f"✅ Found {len(df_raw)} raw results.")
                        st.write("**Columns Detected:**", list(df_raw.columns))
                        
                        st.write(f"**Step 2: Filter Simulation**")
                        has_web = len(df_raw[df_raw['Website'].astype(str).str.contains('http', na=False)])
                        has_phone = len(df_raw[df_raw['Phone'].astype(str).str.len() > 5])
                        st.write(f"- Leads with Website: {has_web}")
                        st.write(f"- Leads with Phone: {has_phone}")
                        
                        no_web_df = df_raw[~df_raw['Website'].astype(str).str.contains('http', na=False)]
                        final_df = no_web_df[no_web_df['Phone'].astype(str).str.len() > 5]
                        st.write(f"- Results matching your filters (No Web + Has Phone): **{len(final_df)}**")
                        
                        if len(final_df) > 0:
                            st.dataframe(final_df.head(3))
                            st.info("💡 If this test worked but your search didn't, try 'Fast (Default)' strategy instead of 'Fastest'.")
                except Exception as e:
                    st.error(f"❌ Diagnostic Crash: {e}")

        st.divider()
        st.markdown("#### 🛠️ Task Management")
        st.button("🧹 Clear Task History", on_click=lambda: st.session_state.pop('last_results', None))

    with tab_results:
        st.markdown("### 💎 Lead Data Warehouse")
        if 'last_results' in st.session_state:
            df = st.session_state['last_results']
            
            # Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Leads Discovered", len(df))
            
            avg_stars = df['Stars'].mean() if 'Stars' in df.columns and not df.empty else 0
            m2.metric("Avg Quality", f"{avg_stars:.1f} ⭐" if avg_stars > 0 else "N/A")
            
            phones = len(df[df['Phone'].astype(str).str.len() > 5]) if 'Phone' in df.columns else 0
            m3.metric("Phone Contacts", phones)
            
            webs = len(df[df['Website'].astype(str).str.contains('http', na=False)]) if 'Website' in df.columns else 0
            m4.metric("Websites Found", webs)

            st.dataframe(df, width="stretch")
            st.markdown(get_csv_download_link(df), unsafe_allow_html=True)
        else:
            st.warning("🕵️ No data in warehouse. Please run an extraction first.")

if __name__ == "__main__":
    main()
