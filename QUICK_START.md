# ✅ Implementation Checklist

Use this checklist to deploy your daily lead generation system.

## Phase 1: Google Cloud Setup (10 minutes)

- [ ] Go to [Google Cloud Console](https://console.cloud.google.com)
- [ ] Create new project (or select existing)
- [ ] Enable **Google Sheets API**
- [ ] Enable **Google Drive API**
- [ ] Navigate to **APIs & Services** → **Credentials**
- [ ] Click **Create Credentials** → **Service Account**
- [ ] Name it: `lead-scraper-bot`
- [ ] Click **Create and Continue**
- [ ] Skip roles (click **Continue**, then **Done**)
- [ ] Click on the service account you just created
- [ ] Go to **Keys** tab
- [ ] Click **Add Key** → **Create new key**
- [ ] Choose **JSON** format
- [ ] Click **Create** (file downloads automatically)
- [ ] **COPY THE SERVICE ACCOUNT EMAIL** (looks like: `lead-scraper-bot@your-project.iam.gserviceaccount.com`)

## Phase 2: Google Sheet Setup (2 minutes)

- [ ] Open your Google Sheet: [https://docs.google.com/spreadsheets/d/1fj3oZLjRhz4dyuUzFrz9hPJ2VazqIySPQjiyrz5rDEs/edit](https://docs.google.com/spreadsheets/d/1fj3oZLjRhz4dyuUzFrz9hPJ2VazqIySPQjiyrz5rDEs/edit)
- [ ] Click **Share** button (top right)
- [ ] Paste the service account email you copied
- [ ] Change permission to **Editor**
- [ ] Uncheck "Notify people" (it's a bot, not a person)
- [ ] Click **Share**

## Phase 3: GitHub Repository Setup (5 minutes)

- [ ] Go to [github.com/Small-Business-Tools/know-your-numbers](https://github.com/Small-Business-Tools/know-your-numbers)
- [ ] Click **Settings** → **Secrets and variables** → **Actions**
- [ ] Click **New repository secret**

**Add these 4 secrets:**

### Secret 1: GOOGLE_SHEETS_CREDS
- [ ] Name: `GOOGLE_SHEETS_CREDS`
- [ ] Value: Open the JSON file you downloaded, **copy the ENTIRE contents**, paste it
- [ ] Click **Add secret**

### Secret 2: SPREADSHEET_ID
- [ ] Name: `SPREADSHEET_ID`
- [ ] Value: `1fj3oZLjRhz4dyuUzFrz9hPJ2VazqIySPQjiyrz5rDEs`
- [ ] Click **Add secret**

### Secret 3: SHEET_NAME
- [ ] Name: `SHEET_NAME`
- [ ] Value: `Prospects`
- [ ] Click **Add secret**

### Secret 4: GOOGLE_MAPS_API_KEY (optional - skip for now)
- [ ] Name: `GOOGLE_MAPS_API_KEY`
- [ ] Value: (leave blank or skip)

## Phase 4: Upload Code to GitHub (5 minutes)

**Option A: Web Upload (Easier)**
- [ ] Download `lead-gen-system.tar.gz` from Claude
- [ ] Extract the archive
- [ ] In GitHub, navigate to your repo
- [ ] For each folder:
  - [ ] Click **Add file** → **Create new file**
  - [ ] Type the full path (e.g., `.github/workflows/daily-lead-gen.yml`)
  - [ ] Paste the file contents
  - [ ] Click **Commit changes**

**Option B: Git Command Line (Faster if you know Git)**
```bash
# Download the archive from Claude first
tar -xzf lead-gen-system.tar.gz
cd know-your-numbers
git add .
git commit -m "Add daily lead generation system"
git push
```

**Files to upload:**
- [ ] `.github/workflows/daily-lead-gen.yml`
- [ ] `scripts/lead_scraper.py`
- [ ] `logs/.gitkeep`
- [ ] `requirements.txt`
- [ ] `SETUP_GUIDE.md`
- [ ] `README.md`
- [ ] `.gitignore`
- [ ] `test-local.sh` (optional - for local testing)

## Phase 5: Test Run (2 minutes)

- [ ] Go to **Actions** tab in GitHub
- [ ] Click on **Daily Lead Generation** workflow (left sidebar)
- [ ] Click **Run workflow** button (right side)
- [ ] Select `main` branch
- [ ] Click green **Run workflow** button
- [ ] Watch the workflow run (takes 3-5 minutes)
- [ ] Check for green checkmark ✅
- [ ] Open your Google Sheet
- [ ] **VERIFY:** New leads should appear at the bottom!

## Phase 6: Verify Automation (1 minute)

- [ ] Confirm workflow ran successfully (green checkmark)
- [ ] Check Google Sheet has new rows
- [ ] Click into the workflow run
- [ ] Click **gather-leads** job
- [ ] Expand **Run lead scraper** step
- [ ] Look for log lines like:
  ```
  ✓ Found: ABC Accountants - info@abcaccountants.co.uk
  ✓ Appended 15 leads to sheet
  SUCCESS: Added 15 new leads to sheet
  ```

## Phase 7: Relax & Monitor (Ongoing)

- [ ] Workflow will run automatically at 7 AM daily
- [ ] Check your Google Sheet each morning
- [ ] Make.com will detect new rows and start outreach
- [ ] Review logs weekly in **Actions** tab

---

## 🚨 Troubleshooting

If the test run fails:

### Error: "Invalid credentials"
- ✅ Check `GOOGLE_SHEETS_CREDS` secret is the FULL JSON (starts with `{` and ends with `}`)
- ✅ Verify you enabled Google Sheets API and Google Drive API

### Error: "Permission denied"
- ✅ Confirm service account email is shared with Editor access on your sheet
- ✅ Check spreadsheet ID is correct: `1fj3oZLjRhz4dyuUzFrz9hPJ2VazqIySPQjiyrz5rDEs`

### Error: "No leads found"
- ✅ This is normal if all scraped leads already exist in your sheet
- ✅ Check logs - it should show "Found X existing emails in sheet"
- ✅ Try adding more towns or categories (see SETUP_GUIDE.md)

### Workflow doesn't run at 7 AM
- ✅ Wait 24 hours - it needs one day to schedule
- ✅ Check GitHub Actions isn't disabled (Settings → Actions → General)
- ✅ Verify cron syntax in workflow file

---

## 🎉 Success Criteria

You're done when:
✅ Test workflow completes with green checkmark  
✅ At least 5-15 new leads appear in Google Sheet  
✅ Logs show "SUCCESS: Added X new leads to sheet"  
✅ Make.com scenario detects the new rows  

---

**Estimated total time: 25 minutes**

**Questions? Check SETUP_GUIDE.md for detailed help**
