name: Daily Lead Generation

on:
  schedule:
    # Runs at 7:00 PM UK time (18:00 UTC in winter, 19:00 UTC in summer)
    - cron: '0 18 * * *'
  workflow_dispatch: # Allows manual trigger for testing

jobs:
  gather-leads:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install gspread oauth2client requests beautifulsoup4 lxml
      
      - name: Run lead scraper
        env:
          GOOGLE_SHEETS_CREDS: ${{ secrets.GOOGLE_SHEETS_CREDS }}
          SPREADSHEET_ID: ${{ secrets.SPREADSHEET_ID }}
          SHEET_NAME: ${{ secrets.SHEET_NAME }}
          GOOGLE_MAPS_API_KEY: ${{ secrets.GOOGLE_MAPS_API_KEY }}
        run: python scripts/lead_scraper.py
      
      - name: Commit results log
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add logs/
          git diff --quiet && git diff --staged --quiet || git commit -m "Daily lead generation: $(date +'%Y-%m-%d')"
          git push || echo "No changes to commit"
