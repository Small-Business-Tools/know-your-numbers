#!/usr/bin/env python3
"""
Daily Lead Scraper for Know Your Numbers
Gathers 15+ small business leads from Wellingborough area
"""

import os
import json
import re
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/scraper_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Target locations - All major Northamptonshire towns
TARGET_TOWNS = [
    # Wellingborough area (primary)
    "Wellingborough",
    "Rushden", 
    "Higham Ferrers",
    "Irthlingborough",
    "Raunds",
    "Finedon",
    # Rest of Northamptonshire
    "Kettering",
    "Corby",
    "Desborough",
    "Rothwell",
    "Burton Latimer",
    "Thrapston",
    "Oundle",
    "Earls Barton"
]

# Business categories to target (small business owners, typically <10 employees)
# NOTE: Accountants and bookkeepers are EXCLUDED - they are competitors/not our target market
BUSINESS_CATEGORIES = [
    "solicitor", "estate agent", "recruitment consultant",
    "marketing agency", "web design", "plumber", "electrician",
    "builder", "garage", "cafe", "restaurant", "personal trainer", "salon",
    "barber", "cleaning service", "independent consultant",
    "mobile mechanic", "driving instructor", "photographer", "florist",
    "chiropractor", "physiotherapist", "dentist", "optician"
]


class LeadScraper:
    def __init__(self):
        self.leads = []
        self.google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        
        # Initialize Google Sheets
        creds_json = os.getenv('GOOGLE_SHEETS_CREDS')
        if not creds_json:
            raise ValueError("GOOGLE_SHEETS_CREDS not set")
        
        creds_dict = json.loads(creds_json)
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        self.gc = gspread.authorize(creds)
        
        self.spreadsheet_id = os.getenv('SPREADSHEET_ID', '1fj3oZLjRhz4dyuUzFrz9hPJ2VazqIySPQjiyrz5rDEs')
        self.sheet_name = os.getenv('SHEET_NAME', 'Prospects')
        
    def get_existing_emails(self) -> set:
        """Fetch all existing emails from Google Sheet to avoid duplicates"""
        try:
            sheet = self.gc.open_by_key(self.spreadsheet_id).worksheet(self.sheet_name)
            all_values = sheet.get_all_values()
            
            # Assuming email is in column C (index 2)
            emails = {row[2].lower().strip() for row in all_values[1:] if len(row) > 2 and row[2]}
            logger.info(f"Found {len(emails)} existing emails in sheet")
            return emails
        except Exception as e:
            logger.error(f"Error fetching existing emails: {e}")
            return set()
    
    def is_small_business(self, business_name: str) -> bool:
        """
        Filter for small businesses (<10 employees)
        Exclude large chains, PLCs, corporate keywords, and accountants/bookkeepers
        """
        # Exclude large company indicators
        exclude_keywords = [
            'PLC', 'LLP', 'LIMITED LIABILITY PARTNERSHIP',
            'GROUP', 'HOLDINGS', 'INTERNATIONAL',
            'CHAIN', 'FRANCHISE', 'CORPORATE',
            'TESCO', 'SAINSBURY', 'ASDA', 'MORRISONS',
            'COSTA', 'STARBUCKS', 'MCDONALDS', 'KFC',
            'BOOTS', 'SUPERDRUG', 'LLOYDS', 'BARCLAYS',
            # EXCLUDE ACCOUNTANTS - Not our target market
            'ACCOUNTANT', 'ACCOUNTANCY', 'ACCOUNTING',
            'BOOKKEEPER', 'BOOKKEEPING', 'BOOK KEEPER',
            'CHARTERED ACCOUNTANT', 'ACCA', 'ACA'
        ]
        
        business_upper = business_name.upper()
        
        # Exclude if contains corporate keywords or accountant-related terms
        if any(keyword in business_upper for keyword in exclude_keywords):
            return False
        
        # Include if it's clearly a local/independent business
        small_biz_indicators = [
            'INDEPENDENT', 'LOCAL', 'FAMILY', 'MOBILE',
            '& SON', '& SONS', '& DAUGHTER', 'BROTHERS',
            "'S ", " SERVICES", " SOLUTIONS"
        ]
        
        # If has small biz indicators, likely good
        if any(indicator in business_upper for indicator in small_biz_indicators):
            return True
        
        # Default: include (we'll manually filter if needed)
        return True
    
    def extract_email_from_text(self, text: str) -> Optional[str]:
        """Extract email address from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None
    
    def scrape_google_search(self, business_name: str, town: str) -> Optional[Dict]:
        """
        Scrape Google search results for business email
        Format: "Business Name" Town email OR gmail OR hotmail
        """
        try:
            query = f'"{business_name}" {town} email OR gmail OR hotmail'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Use DuckDuckGo instead of Google (no CAPTCHA)
            url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Extract snippets
                snippets = soup.find_all('a', class_='result__snippet')
                
                for snippet in snippets[:3]:  # Check first 3 results
                    text = snippet.get_text()
                    email = self.extract_email_from_text(text)
                    
                    if email and not any(x in email.lower() for x in ['example', 'google', 'schema']):
                        return {'email': email, 'source': 'google_search'}
            
            time.sleep(2)  # Be respectful
            
        except Exception as e:
            logger.warning(f"Error in Google search for {business_name}: {e}")
        
        return None
    
    def scrape_yell_directory(self, category: str, town: str) -> List[Dict]:
        """Scrape Yell.com business directory"""
        leads = []
        
        try:
            # Yell.com search URL
            url = f"https://www.yell.com/ucs/UcsSearchAction.do?keywords={category}&location={town}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find business listings
            businesses = soup.find_all('div', class_='businessCapsule--mainContent')
            
            for biz in businesses[:3]:  # Limit per category
                try:
                    name_elem = biz.find('h2', class_='businessCapsule--name')
                    business_name = name_elem.get_text(strip=True) if name_elem else None
                    
                    if not business_name:
                        continue
                    
                    # Try to find email on detail page
                    detail_link = name_elem.find('a')['href'] if name_elem and name_elem.find('a') else None
                    
                    if detail_link:
                        detail_url = f"https://www.yell.com{detail_link}"
                        detail_response = requests.get(detail_url, headers=headers, timeout=10)
                        detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                        
                        # Look for email in page content
                        page_text = detail_soup.get_text()
                        email = self.extract_email_from_text(page_text)
                        
                        if email:
                            leads.append({
                                'name': '',  # Owner name not available from Yell
                                'business': business_name,
                                'email': email,
                                'source': 'yell',
                                'town': town
                            })
                        
                        time.sleep(1)  # Rate limiting
                
                except Exception as e:
                    logger.warning(f"Error parsing Yell business: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping Yell for {category} in {town}: {e}")
        
        return leads
    
    def search_companies_house(self, postcode_prefix: str = "NN") -> List[Dict]:
        """
        Search Companies House for small limited companies
        Free API, no key required for basic search
        """
        leads = []
        
        try:
            # Companies House API endpoint (free tier)
            url = "https://api.company-information.service.gov.uk/search/companies"
            params = {
                'q': f'{postcode_prefix}*',  # Northamptonshire postcodes
                'items_per_page': 20
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for company in data.get('items', [])[:10]:
                    # Only target small Ltd companies (not PLCs or large orgs)
                    if 'LTD' in company.get('title', '').upper():
                        company_name = company.get('title')
                        company_number = company.get('company_number')
                        
                        # Try to find director/owner info and email via search
                        search_result = self.scrape_google_search(company_name, "Wellingborough")
                        
                        if search_result and search_result.get('email'):
                            leads.append({
                                'name': '',  # Owner name requires separate API call
                                'business': company_name,
                                'email': search_result['email'],
                                'source': 'companies_house',
                                'town': 'Wellingborough'
                            })
                        
                        time.sleep(2)
        
        except Exception as e:
            logger.error(f"Error with Companies House API: {e}")
        
        return leads
    
    def gather_leads(self, target_count: int = 15) -> List[Dict]:
        """Main lead gathering function"""
        logger.info(f"Starting lead generation - target: {target_count} leads")
        
        existing_emails = self.get_existing_emails()
        collected_leads = []
        
        # Method 1: Yell.com directory scraping
        logger.info("Scraping Yell.com directory...")
        for town in TARGET_TOWNS[:2]:  # Start with 2 towns
            for category in BUSINESS_CATEGORIES[:3]:  # Try 3 categories per town
                if len(collected_leads) >= target_count:
                    break
                
                logger.info(f"Searching for {category} in {town}...")
                yell_leads = self.scrape_yell_directory(category, town)
                
                for lead in yell_leads:
                    # Filter for small businesses only
                    if not self.is_small_business(lead.get('business', '')):
                        logger.info(f"⊘ Skipped (large/chain): {lead['business']}")
                        continue
                    
                    if lead['email'].lower() not in existing_emails:
                        collected_leads.append(lead)
                        existing_emails.add(lead['email'].lower())
                        logger.info(f"✓ Found: {lead['business']} - {lead['email']}")
                
                time.sleep(2)
        
        # Method 2: Companies House + Google search
        if len(collected_leads) < target_count:
            logger.info("Searching Companies House...")
            ch_leads = self.search_companies_house()
            
            for lead in ch_leads:
                if len(collected_leads) >= target_count:
                    break
                
                # Filter for small businesses
                if not self.is_small_business(lead.get('business', '')):
                    continue
                
                if lead['email'].lower() not in existing_emails:
                    collected_leads.append(lead)
                    existing_emails.add(lead['email'].lower())
                    logger.info(f"✓ Found: {lead['business']} - {lead['email']}")
        
        logger.info(f"Lead generation complete. Found {len(collected_leads)} new leads")
        return collected_leads
    
    def append_to_sheet(self, leads: List[Dict]):
        """Append leads to Google Sheet"""
        if not leads:
            logger.info("No leads to append")
            return
        
        try:
            sheet = self.gc.open_by_key(self.spreadsheet_id).worksheet(self.sheet_name)
            
            # Format: Name, Business, Email, Date Added, Email 1 Sent, Email 2 Sent, Email 3 Sent, Status, Next Action Date, Notes
            rows_to_append = []
            today = datetime.now().strftime('%Y-%m-%d')
            
            for lead in leads:
                row = [
                    lead.get('name', ''),
                    lead.get('business', ''),
                    lead.get('email', ''),
                    today,
                    '',  # Email 1 Sent
                    '',  # Email 2 Sent
                    '',  # Email 3 Sent
                    'New',  # Status
                    '',  # Next Action Date
                    f"Source: {lead.get('source', 'unknown')}"  # Notes
                ]
                rows_to_append.append(row)
            
            # Append all rows at once
            sheet.append_rows(rows_to_append)
            logger.info(f"✓ Appended {len(rows_to_append)} leads to sheet")
            
        except Exception as e:
            logger.error(f"Error appending to sheet: {e}")
            raise


def main():
    """Main execution"""
    try:
        scraper = LeadScraper()
        leads = scraper.gather_leads(target_count=15)
        
        if leads:
            scraper.append_to_sheet(leads)
            logger.info(f"SUCCESS: Added {len(leads)} new leads to sheet")
        else:
            logger.warning("No new leads found today")
        
        # Save summary
        summary = {
            'date': datetime.now().isoformat(),
            'leads_found': len(leads),
            'leads': [{'business': l['business'], 'email': l['email']} for l in leads]
        }
        
        with open(f'logs/summary_{datetime.now().strftime("%Y%m%d")}.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
    except Exception as e:
        logger.error(f"FATAL ERROR: {e}")
        raise


if __name__ == "__main__":
    main()
