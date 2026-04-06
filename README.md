# ⚡ QUICK SETUP CARD

## What You Need

1. **Your Google Sheets URL** ← Paste it here: _________________
   
   Extract the ID from URL like this:
   ```
   https://docs.google.com/spreadsheets/d/[THIS_IS_THE_ID]/edit
   ```

2. **Google Service Account JSON** (download from Google Cloud Console)

3. **5 minutes**

---

## The 3-Step Setup

### Step 1: Google Cloud (3 min)
```
console.cloud.google.com
→ Enable Google Sheets API
→ Create Service Account
→ Download JSON key
→ Copy service account email
```

### Step 2: Share Your Sheet (30 sec)
```
Open your Google Sheet
→ Click Share
→ Paste service account email
→ Give Editor access
→ Share
```

### Step 3: GitHub Secrets (90 sec)
```
GitHub repo → Settings → Secrets
→ Add GOOGLE_SHEETS_CREDS (paste full JSON)
→ Add SPREADSHEET_ID (from your URL)
→ Add SHEET_NAME (usually "Prospects")
→ Done!
```

---

## Upload These Files to GitHub

```
.github/workflows/daily-lead-gen.yml
scripts/lead_scraper.py
logs/.gitkeep
requirements.txt
.gitignore
```

Easiest method: Use GitHub web interface → "Add file" → "Upload files"

---

## Test It

```
GitHub → Actions → Daily Lead Generation
→ Run workflow
→ Wait 3-5 minutes
→ Check your Google Sheet ✅
```

---

## It Will Run

⏰ **Every day at 7:00 PM UK time**

📊 **Adds 15+ new leads to your sheet**

🎯 **Targets: Small Northamptonshire businesses (<10 employees)**

✅ **Automatically checks for duplicates**

---

## Your Sheet Columns (from screenshot)

| Name | Business | Email | Date Added | Email 1 Sent | Email 2 Sent | Email 3 Sent | Status | Next Action Date | Notes |
|------|----------|-------|------------|--------------|--------------|--------------|--------|------------------|-------|

The script will populate:
- **Business** ✓
- **Email** ✓  
- **Date Added** ✓
- **Status** = "New" ✓
- **Notes** = "Source: yell" etc. ✓

(Name is left blank - most sources don't provide owner names)

---

## Troubleshooting

❌ **"Invalid credentials"**  
→ Check GOOGLE_SHEETS_CREDS is the FULL JSON (starts with `{`)

❌ **"Permission denied"**  
→ Share the sheet with your service account email (Editor access)

❌ **"No leads found"**  
→ Normal if all leads already exist. Check logs for details.

---

## Questions?

📖 Read **SETUP_GUIDE.md** for detailed help  
📋 Follow **IMPLEMENTATION_CHECKLIST.md** step-by-step  
📂 All files in `lead-generation-system/` folder

**You've got this! 🚀**
