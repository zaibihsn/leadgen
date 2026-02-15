@echo off
echo Installing dependencies...
pip install -r requirements.txt
echo Installing Playwright browsers...
playwright install chromium
echo Setup complete! To run the app, use: streamlit run app.py
pause
