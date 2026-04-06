#!/bin/bash
# Local testing script for lead scraper
# Run this BEFORE pushing to GitHub to test locally

echo "🧪 Testing Lead Scraper Locally"
echo "================================"
echo ""

# Check if credentials file exists
if [ ! -f "service-account-key.json" ]; then
    echo "❌ Error: service-account-key.json not found"
    echo ""
    echo "Please:"
    echo "1. Download your Google Service Account JSON key"
    echo "2. Save it as 'service-account-key.json' in this folder"
    echo "3. DO NOT commit this file to Git (it's in .gitignore)"
    exit 1
fi

# Set environment variables
export GOOGLE_SHEETS_CREDS=$(cat service-account-key.json)
export SPREADSHEET_ID="1fj3oZLjRhz4dyuUzFrz9hPJ2VazqIySPQjiyrz5rDEs"
export SHEET_NAME="Prospects"

echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "🔍 Running lead scraper..."
echo ""

python scripts/lead_scraper.py

echo ""
echo "✅ Test complete! Check logs/ folder for results"
echo ""
echo "Next step: Upload to GitHub and set up secrets"
