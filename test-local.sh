# Daily Lead Generation Setup Guide

This system automatically scrapes 15+ small business leads daily from Wellingborough and surrounding areas, checks for duplicates, and adds them to your Google Sheet.

## Quick Start (5 minutes)

### 1. Set Up Google Sheets API Access

**Create Service Account:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or use existing)
3. Enable **Google Sheets API** and **Google Drive API**
4. Create credentials → Service Account
5. Create a key (JSON format) and download it
6. Copy the service account email (looks like: `xyz@project-name.iam.gserviceaccount.com`)

**Share Your Sheet:**
1. Open your Google Sheet: `1fj3oZLjRhz4dyuUzFrz9hPJ2VazqIySPQjiyrz5rDEs`
2. Click "Share" button
3. Paste the service account email
4. Give "Editor" access

### 2. Add GitHub Secrets

In your GitHub repository (`Small-Business-Tools/know-your-numbers`):

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `GOOGLE_SHEETS_CREDS` | Paste the ENTIRE contents of the JSON file you downloaded |
| `SPREADSHEET_ID` | `1fj3oZLjRhz4dyuUzFrz9hPJ2VazqIySPQjiyrz5rDEs` |
| `SHEET_NAME` | `Prospects` |
| `GOOGLE_MAPS_API_KEY` | *(Optional - leave blank for now)* |

### 3. Upload Files to GitHub

Upload these files to your repository:

```
know-your-numbers/
├── .github/
│   └── workflows/
│       └── daily-lead-gen.yml
├── scripts/
│   └── lead_scraper.py
├── logs/
│   └── .gitkeep
└── requirements.txt
```

**Via GitHub Web Interface:**
1. Navigate to your repo
2. Click "Add file" → "Upload files"
3. Drag all folders/files
4. Commit changes

**Or via Git command line:**
```bash
git clone https://github.com/Small-Business-Tools/know-your-numbers.git
cd know-your-numbers
# Copy the files from this setup into the repo
git add .
git commit -m "Add daily lead generation workflow"
git push
```

### 4. Test the Workflow

**Manual test:**
1. Go to **Actions** tab in GitHub
2. Click **Daily Lead Generation**
3. Click **Run workflow**
4. Watch it run (takes 3-5 minutes)
5. Check your Google Sheet for new leads!

**Automatic schedule:**
- Runs daily at **7:00 AM UK time**
- No action needed from you

---

## How It Works

### Lead Sources

1. **Yell.com Directory** (primary source)
   - Scrapes business listings for Wellingborough area
   - Targets: accountants, solicitors, cafes, gyms, etc.
   - Extracts emails from business detail pages

2. **Companies House API** (secondary source)
   - Searches for Ltd companies with NN postcodes (Northamptonshire)
   - Cross-references with Google search to find emails

3. **Google Search via DuckDuckGo** (email finding)
   - Format: `"Business Name" Town email OR gmail OR hotmail`
   - Extracts email addresses from search snippets

### Duplicate Prevention

- Fetches all existing emails from your Google Sheet
- Checks every new lead against existing list
- Only adds genuinely new prospects

### Data Added to Sheet

For each lead found, the script adds:
- **Name:** (Currently blank - most sources don't provide owner names)
- **Business:** Company/business name
- **Email:** Contact email address
- **Date Added:** Today's date
- **Email 1/2/3 Sent:** (Blank - ready for your Make.com outreach)

---

## Configuration Options

### Change Run Time

Edit `.github/workflows/daily-lead-gen.yml`:

```yaml
schedule:
  - cron: '0 6 * * *'  # Change this line
```

**Cron format:** `minute hour day month weekday`
- `0 6 * * *` = 6:00 AM UTC (7:00 AM UK time in winter)
- `0 9 * * *` = 9:00 AM UTC (10:00 AM UK time)
- `30 14 * * 1-5` = 2:30 PM UTC, Monday-Friday only

### Change Target Towns

Edit `scripts/lead_scraper.py`:

```python
TARGET_TOWNS = [
    "Wellingborough",
    "Rushden",
    "Kettering",  # Add more
    "Corby",      # Add more
]
```

### Change Business Categories

Edit `scripts/lead_scraper.py`:

```python
BUSINESS_CATEGORIES = [
    "accountant",
    "solicitor",
    "your custom category",  # Add more
]
```

### Change Daily Target

Edit `scripts/lead_scraper.py` (line ~290):

```python
leads = scraper.gather_leads(target_count=20)  # Change from 15 to your target
```

---

## Monitoring & Logs

### View Logs
1. Go to **Actions** tab in GitHub
2. Click on a workflow run
3. Click **gather-leads** job
4. Expand **Run lead scraper** step

### Download Full Logs
- Logs are saved in `logs/` folder in your repo
- Format: `scraper_YYYYMMDD.log`
- Summary JSON: `summary_YYYYMMDD.json`

### Typical Log Output
```
2024-01-15 07:00:01 - INFO - Starting lead generation - target: 15 leads
2024-01-15 07:00:02 - INFO - Found 26 existing emails in sheet
2024-01-15 07:00:05 - INFO - Scraping Yell.com directory...
2024-01-15 07:00:10 - INFO - ✓ Found: ABC Accountants - info@abcaccountants.co.uk
...
2024-01-15 07:03:45 - INFO - Lead generation complete. Found 15 new leads
2024-01-15 07:03:47 - INFO - ✓ Appended 15 leads to sheet
2024-01-15 07:03:47 - INFO - SUCCESS: Added 15 new leads to sheet
```

---

## Troubleshooting

### "No leads found today"
- **Cause:** All scraped leads already exist in sheet OR scraping blocked
- **Fix:** 
  - Expand `TARGET_TOWNS` to include more areas
  - Add more `BUSINESS_CATEGORIES`
  - Check logs for blocking/errors

### "Error fetching existing emails"
- **Cause:** Google Sheets credentials incorrect
- **Fix:** 
  - Re-check service account email is shared with sheet
  - Verify `GOOGLE_SHEETS_CREDS` secret is the full JSON (starts with `{`)

### "403 Forbidden" errors
- **Cause:** Google Sheets API not enabled
- **Fix:** Enable Google Sheets API in Google Cloud Console

### "Rate limit" or "Too many requests"
- **Cause:** Hitting website rate limits
- **Fix:** Increase `time.sleep()` delays in script (already set to 2 seconds)

### Workflow not running automatically
- **Cause:** GitHub Actions disabled for free accounts with no activity
- **Fix:** Make a commit to your repo monthly to keep Actions alive

---

## Cost Analysis

| Component | Cost |
|-----------|------|
| GitHub Actions | **FREE** (2,000 minutes/month for free accounts) |
| Google Sheets API | **FREE** (unlimited for service accounts) |
| Companies House API | **FREE** (basic search) |
| Web scraping | **FREE** |
| **Total** | **£0/month** |

**This workflow uses ~5 minutes/day = 150 minutes/month (well within free tier)**

---

## Next Steps

Once this is working:

1. **Make.com Integration:** Your Make.com scenario already watches this sheet and triggers email sequences
2. **Manual enrichment:** For leads without names, manually research the owner on LinkedIn/company website
3. **Expand sources:** Add more business directories (Thomson Local, Bing Places, etc.)
4. **Google Maps API:** Add `GOOGLE_MAPS_API_KEY` secret to unlock richer business data (£150 free credit/month)

---

## Support

If you hit issues:
1. Check the **Actions** logs first
2. Verify all GitHub secrets are set correctly
3. Confirm service account has Editor access to your sheet
4. Test with manual "Run workflow" before relying on schedule

The script is designed to fail gracefully - if one source fails, it tries others. Check logs to see which sources are working.
