#!/usr/bin/env python3
"""
Enhanced Lead Scraper for Know Your Numbers
Finds business websites, then scrapes emails from contact pages
"""

import os
import json
import re
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
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
    "Wellingborough", "Rushden", "Higham Ferrers", "Irthlingborough",
    "Raunds", "Finedon", "Kettering", "Corby", "Desborough",
    "Rothwell", "Burton Latimer", "Thrapston", "Oundle", "Earls Barton"
]

# Business categories - ACCOUNTANTS EXCLUDED
BUSINESS_CATEGORIES = [
    "solicitor", "estate agent", "recruitment consultant",
    "marketing agency", "web design", "plumber", "electrician",
    "builder", "garage", "cafe", "restaurant", "personal trainer", "salon",
    "barber", "cleaning service", "independent consultant",
    "mobile mechanic", "driving instructor", "photographer", "florist",
    "chiropractor", "physiotherapist", "dentist", "optician"
]


class EnhancedLeadScraper:
    def __init__(self):
        self.leads = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
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
            emails = {row[2].lower().strip() for row in all_values[1:] if len(row) > 2 and row[2]}
            logger.info(f"Found {len(emails)} existing emails in sheet")
            return emails
        except Exception as e:
            logger.error(f"Error fetching existing emails: {e}")
            return set()
    
    def is_small_business(self, business_name: str) -> bool:
        """Filter for small businesses, exclude chains and accountants"""
        exclude_keywords = [
            'PLC', 'LLP', 'GROUP', 'HOLDINGS', 'INTERNATIONAL', 'CHAIN', 'FRANCHISE',
            'TESCO', 'SAINSBURY', 'ASDA', 'MORRISONS', 'COSTA', 'STARBUCKS',
            'MCDONALDS', 'KFC', 'BOOTS', 'SUPERDRUG', 'LLOYDS', 'BARCLAYS',
            'ACCOUNTANT', 'ACCOUNTANCY', 'ACCOUNTING', 'BOOKKEEPER', 'BOOKKEEPING',
            'CHARTERED ACCOUNTANT', 'ACCA', 'ACA'
        ]
        
        business_upper = business_name.upper()
        if any(keyword in business_upper for keyword in exclude_keywords):
            return False
        return True
    
    def extract_emails_from_text(self, text: str) -> List[str]:
        """Extract all email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        # Filter out common fake/example emails
        valid_emails = [
            e for e in emails 
            if not any(x in e.lower() for x in ['example', 'test', 'spam', 'noreply', 'sentry'])
        ]
        return valid_emails
    
    def find_contact_page_urls(self, base_url: str, soup: BeautifulSoup) -> List[str]:
        """Find contact/about page URLs"""
        contact_keywords = ['contact', 'about', 'get-in-touch', 'reach-us', 'find-us']
        contact_urls = []
        
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            text = link.get_text().lower()
            
            if any(keyword in href or keyword in text for keyword in contact_keywords):
                full_url = urljoin(base_url, link['href'])
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    contact_urls.append(full_url)
        
        return list(set(contact_urls))[:3]  # Max 3 contact pages
    
    def scrape_website_for_email(self, website_url: str) -> Optional[str]:
        """Visit a website and scrape for email addresses"""
        try:
            # Normalize URL
            if not website_url.startswith('http'):
                website_url = 'https://' + website_url
            
            logger.info(f"  → Checking website: {website_url}")
            
            # Try homepage first
            response = self.session.get(website_url, timeout=15, allow_redirects=True)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check homepage for emails
            homepage_text = soup.get_text()
            emails = self.extract_emails_from_text(homepage_text)
            
            if emails:
                logger.info(f"  ✓ Found email on homepage: {emails[0]}")
                return emails[0]
            
            # If no email on homepage, check contact pages
            contact_urls = self.find_contact_page_urls(website_url, soup)
            
            for contact_url in contact_urls:
                try:
                    contact_response = self.session.get(contact_url, timeout=10)
                    if contact_response.status_code == 200:
                        contact_soup = BeautifulSoup(contact_response.text, 'html.parser')
                        contact_text = contact_soup.get_text()
                        emails = self.extract_emails_from_text(contact_text)
                        
                        if emails:
                            logger.info(f"  ✓ Found email on contact page: {emails[0]}")
                            return emails[0]
                    
                    time.sleep(1)
                except:
                    continue
            
            # Fallback: try common email patterns
            domain = urlparse(website_url).netloc.replace('www.', '')
            common_emails = [f'info@{domain}', f'hello@{domain}', f'contact@{domain}']
            
            logger.info(f"  → No email found, using fallback: {common_emails[0]}")
            return common_emails[0]
            
        except Exception as e:
            logger.warning(f"  ✗ Error scraping website {website_url}: {e}")
            return None
    
    def scrape_yell_with_websites(self, category: str, town: str) -> List[Dict]:
        """Scrape Yell.com and extract business websites"""
        leads = []
        
        try:
            url = f"https://www.yell.com/ucs/UcsSearchAction.do?keywords={category}&location={town}"
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find business listings
            businesses = soup.find_all('div', class_='businessCapsule--mainContent')
            
            for biz in businesses[:5]:  # Check first 5 businesses
                try:
                    name_elem = biz.find('h2', class_='businessCapsule--name')
                    business_name = name_elem.get_text(strip=True) if name_elem else None
                    
                    if not business_name or not self.is_small_business(business_name):
                        continue
                    
                    # Get business detail page
                    detail_link = name_elem.find('a')['href'] if name_elem and name_elem.find('a') else None
                    
                    if detail_link:
                        detail_url = f"https://www.yell.com{detail_link}"
                        detail_response = self.session.get(detail_url, timeout=10)
                        detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                        
                        # Look for website link
                        website_link = detail_soup.find('a', class_='text-nowrap--md')
                        if website_link and 'href' in website_link.attrs:
                            website_url = website_link['href']
                            
                            # Scrape the actual business website for email
                            email = self.scrape_website_for_email(website_url)
                            
                            if email:
                                leads.append({
                                    'name': '',
                                    'business': business_name,
                                    'email': email,
                                    'source': 'yell+website',
                                    'town': town,
                                    'website': website_url
                                })
                        
                        time.sleep(2)  # Be respectful
                
                except Exception as e:
                    logger.warning(f"Error parsing Yell business: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping Yell for {category} in {town}: {e}")
        
        return leads
    
    def search_google_for_business(self, business_type: str, town: str) -> List[Dict]:
        """Search Google for businesses and their websites"""
        leads = []
        
        try:
            # Use DuckDuckGo HTML search (no API needed)
            query = f"{business_type} {town} Northamptonshire"
            url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
            
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract search results
            results = soup.find_all('a', class_='result__a')[:5]
            
            for result in results:
                try:
                    result_url = result.get('href', '')
                    business_name = result.get_text(strip=True)
                    
                    if not business_name or not self.is_small_business(business_name):
                        continue
                    
                    # Extract actual website URL
                    if result_url and 'uddg=' in result_url:
                        website_url = result_url.split('uddg=')[1].split('&')[0]
                        
                        # Skip Yell, directories, Facebook (we want real websites)
                        if any(x in website_url for x in ['yell.com', 'facebook.com', 'linkedin.com', '192.com']):
                            continue
                        
                        email = self.scrape_website_for_email(website_url)
                        
                        if email:
                            leads.append({
                                'name': '',
                                'business': business_name,
                                'email': email,
                                'source': 'google+website',
                                'town': town,
                                'website': website_url
                            })
                    
                    time.sleep(2)
                
                except Exception as e:
                    continue
        
        except Exception as e:
            logger.error(f"Error in Google search: {e}")
        
        return leads
    
    def gather_leads(self, target_count: int = 15) -> List[Dict]:
        """Main lead gathering function with website scraping"""
        logger.info(f"Starting ENHANCED lead generation - target: {target_count} leads")
        
        existing_emails = self.get_existing_emails()
        collected_leads = []
        
        # Method 1: Yell.com with website scraping
        logger.info("Method 1: Yell.com directory with website scraping...")
        for town in TARGET_TOWNS[:4]:  # 4 towns
            for category in BUSINESS_CATEGORIES[:6]:  # 6 categories
                if len(collected_leads) >= target_count:
                    break
                
                logger.info(f"Searching for {category} in {town}...")
                yell_leads = self.scrape_yell_with_websites(category, town)
                
                for lead in yell_leads:
                    if lead['email'].lower() not in existing_emails:
                        collected_leads.append(lead)
                        existing_emails.add(lead['email'].lower())
                        logger.info(f"✓ FOUND: {lead['business']} - {lead['email']}")
                
                if len(collected_leads) >= target_count:
                    break
        
        # Method 2: Google search with website scraping
        if len(collected_leads) < target_count:
            logger.info("Method 2: Google search with website scraping...")
            for town in TARGET_TOWNS[:3]:
                for category in BUSINESS_CATEGORIES[:4]:
                    if len(collected_leads) >= target_count:
                        break
                    
                    logger.info(f"Google searching for {category} in {town}...")
                    google_leads = self.search_google_for_business(category, town)
                    
                    for lead in google_leads:
                        if lead['email'].lower() not in existing_emails:
                            collected_leads.append(lead)
                            existing_emails.add(lead['email'].lower())
                            logger.info(f"✓ FOUND: {lead['business']} - {lead['email']}")
        
        logger.info(f"Lead generation complete. Found {len(collected_leads)} new leads")
        return collected_leads
    
    def append_to_sheet(self, leads: List[Dict]):
        """Append leads to Google Sheet"""
        if not leads:
            logger.info("No leads to append")
            return
        
        try:
            sheet = self.gc.open_by_key(self.spreadsheet_id).worksheet(self.sheet_name)
            
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
                    f"Source: {lead.get('source', 'unknown')} | Website: {lead.get('website', 'N/A')}"
                ]
                rows_to_append.append(row)
            
            sheet.append_rows(rows_to_append)
            logger.info(f"✓ Appended {len(rows_to_append)} leads to sheet")
            
        except Exception as e:
            logger.error(f"Error appending to sheet: {e}")
            raise


def main():
    """Main execution"""
    try:
        scraper = EnhancedLeadScraper()
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
            'leads': [{'business': l['business'], 'email': l['email'], 'website': l.get('website', 'N/A')} for l in leads]
        }
        
        with open(f'logs/summary_{datetime.now().strftime("%Y%m%d")}.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
    except Exception as e:
        logger.error(f"FATAL ERROR: {e}")
        raise


if __name__ == "__main__":
    main()
