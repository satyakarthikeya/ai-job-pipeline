#!/usr/bin/env python3
"""
Indian Job Boards Scraper
Focused scrapers for Naukri, Unstop, and Internshala
Targeting AI, ML, Data Science, MLOps, Cloud internships in India
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
from typing import List, Dict
from urllib.parse import quote_plus

# User agents for anti-detection
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

# Search terms for AI/ML/Data/Cloud domain
SEARCH_TERMS = [
    "AI intern",
    "Machine Learning intern", 
    "Data Science intern",
    "MLOps intern",
    "Data Analyst intern",
    "Cloud intern",
    "Deep Learning intern",
    "NLP intern",
    "Data Engineer intern",
]


def get_headers():
    """Get randomized headers"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }


def scrape_naukri(search_term: str, max_results: int = 20) -> List[Dict]:
    """
    Scrape Naukri.com for internships
    
    Args:
        search_term: Job search term
        max_results: Maximum results to fetch
        
    Returns:
        List of job dictionaries
    """
    jobs = []
    
    try:
        # Naukri search URL format
        query = quote_plus(search_term)
        url = f"https://www.naukri.com/{query.replace('+', '-')}-jobs"
        
        print(f"[Naukri] Searching: {search_term}")
        
        response = requests.get(url, headers=get_headers(), timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find job cards - Naukri uses article tags with class
            job_cards = soup.find_all('article', class_='jobTuple')
            
            if not job_cards:
                # Try alternate selectors
                job_cards = soup.find_all('div', {'class': lambda x: x and 'jobTuple' in x})
            
            for card in job_cards[:max_results]:
                try:
                    # Extract job details
                    title_elem = card.find('a', class_='title')
                    company_elem = card.find('a', class_='subTitle')
                    location_elem = card.find('li', class_='location')
                    exp_elem = card.find('li', class_='experience')
                    
                    title = title_elem.get_text(strip=True) if title_elem else None
                    company = company_elem.get_text(strip=True) if company_elem else 'Unknown'
                    location = location_elem.get_text(strip=True) if location_elem else 'India'
                    experience = exp_elem.get_text(strip=True) if exp_elem else ''
                    url = title_elem.get('href', '') if title_elem else ''
                    
                    if title:
                        job = {
                            'title': title,
                            'company': company,
                            'location': location,
                            'url': url if url.startswith('http') else f"https://www.naukri.com{url}",
                            'description': f"Experience: {experience}",
                            'source': 'naukri',
                            'posted_date': datetime.now().strftime('%Y-%m-%d'),
                            'experience': experience
                        }
                        jobs.append(job)
                        
                except Exception as e:
                    continue
                    
        print(f"[Naukri] Found {len(jobs)} jobs for '{search_term}'")
        
    except Exception as e:
        print(f"[Naukri] Error: {e}")
    
    return jobs


def scrape_unstop(search_term: str = None, max_results: int = 50) -> List[Dict]:
    """
    Scrape Unstop for internships using their public API
    
    Args:
        search_term: Optional search term (not used - API returns all internships)
        max_results: Maximum results
        
    Returns:
        List of job dictionaries
    """
    jobs = []
    
    try:
        # Unstop API - get all internships
        url = 'https://unstop.com/api/public/opportunity/search-result?opportunity=internships&per_page=50'
        
        print(f"[Unstop] Fetching internships...")
        
        headers = get_headers()
        headers['Accept'] = 'application/json'
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            opportunities = data.get('data', {}).get('data', [])
            
            for opp in opportunities[:max_results]:
                try:
                    title = opp.get('title', '')
                    
                    # Get organization info
                    org = opp.get('organisation', {})
                    company = org.get('name', 'Unknown') if isinstance(org, dict) else 'Unknown'
                    
                    # Get location from locations array
                    locations = opp.get('locations', [])
                    if locations and isinstance(locations, list):
                        location_names = [loc.get('city', '') for loc in locations if isinstance(loc, dict)]
                        location = ', '.join(filter(None, location_names)) or 'India'
                    else:
                        location = 'India'
                    
                    # Build URL
                    slug = opp.get('public_url', '') or opp.get('seo_url', '')
                    job_url = f"https://unstop.com{slug}" if slug and not slug.startswith('http') else slug
                    
                    # Get job details
                    job_detail = opp.get('jobDetail', {}) or {}
                    stipend = job_detail.get('stipend', '')
                    
                    job = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'url': job_url,
                        'description': '',
                        'source': 'unstop',
                        'posted_date': opp.get('approved_date', ''),
                        'type': opp.get('type', 'internship'),
                        'stipend': stipend
                    }
                    jobs.append(job)
                    
                except Exception as e:
                    continue
                    
        print(f"[Unstop] Found {len(jobs)} internships")
        
    except Exception as e:
        print(f"[Unstop] Error: {e}")
    
    return jobs


def scrape_internshala(search_term: str, max_results: int = 20) -> List[Dict]:
    """
    Scrape Internshala for internships
    
    Args:
        search_term: Search term
        max_results: Maximum results
        
    Returns:
        List of job dictionaries
    """
    jobs = []
    
    try:
        # Internshala URL format
        query = search_term.lower().replace(' ', '-')
        url = f"https://internshala.com/internships/{query}-internship"
        
        print(f"[Internshala] Searching: {search_term}")
        
        response = requests.get(url, headers=get_headers(), timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find internship cards - correct selector
            cards = soup.find_all('div', class_='individual_internship')
            
            print(f"[Internshala] Found {len(cards)} cards")
            
            for card in cards[:max_results]:
                try:
                    # Title and URL
                    title_elem = card.find('a', class_='job-title-href')
                    title = title_elem.get_text(strip=True) if title_elem else None
                    job_url = title_elem.get('href', '') if title_elem else ''
                    if job_url and not job_url.startswith('http'):
                        job_url = f"https://internshala.com{job_url}"
                    
                    # Company
                    company_elem = card.find('p', class_='company-name')
                    if not company_elem:
                        company_elem = card.find('a', class_='link_display_like_text')
                    company = company_elem.get_text(strip=True) if company_elem else 'Unknown'
                    
                    # Location
                    location_elem = card.find('p', id='location_names')
                    if not location_elem:
                        location_elem = card.find('div', class_='locations')
                    location = location_elem.get_text(strip=True) if location_elem else 'India'
                    
                    # Stipend
                    stipend_elem = card.find('span', class_='stipend')
                    stipend = stipend_elem.get_text(strip=True) if stipend_elem else ''
                    
                    if title:
                        job = {
                            'title': title,
                            'company': company,
                            'location': location,
                            'url': job_url,
                            'description': f"Stipend: {stipend}" if stipend else '',
                            'source': 'internshala',
                            'posted_date': datetime.now().strftime('%Y-%m-%d'),
                            'stipend': stipend
                        }
                        jobs.append(job)
                        
                except Exception as e:
                    continue
                    
        print(f"[Internshala] Found {len(jobs)} internships for '{search_term}'")
        
    except Exception as e:
        print(f"[Internshala] Error: {e}")
    
    return jobs


def scrape_wellfound(search_term: str, max_results: int = 15) -> List[Dict]:
    """
    Scrape Wellfound (AngelList) for startup jobs
    Good for AI/ML roles at startups
    """
    jobs = []
    
    try:
        # Wellfound has a GraphQL API but we'll use the search page
        query = quote_plus(search_term)
        url = f"https://wellfound.com/role/l/software-engineer/{query}"
        
        print(f"[Wellfound] Searching: {search_term}")
        
        response = requests.get(url, headers=get_headers(), timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Parse job listings
            job_cards = soup.find_all('div', {'class': lambda x: x and 'styles_component' in str(x)})
            
            for card in job_cards[:max_results]:
                try:
                    title_elem = card.find('a', {'class': lambda x: x and 'styles_jobTitle' in str(x)})
                    company_elem = card.find('span', {'class': lambda x: x and 'styles_companyName' in str(x)})
                    
                    if title_elem:
                        job = {
                            'title': title_elem.get_text(strip=True),
                            'company': company_elem.get_text(strip=True) if company_elem else 'Startup',
                            'location': 'Remote / India',
                            'url': f"https://wellfound.com{title_elem.get('href', '')}",
                            'description': '',
                            'source': 'wellfound',
                            'posted_date': datetime.now().strftime('%Y-%m-%d')
                        }
                        jobs.append(job)
                        
                except Exception as e:
                    continue
                    
        print(f"[Wellfound] Found {len(jobs)} jobs for '{search_term}'")
        
    except Exception as e:
        print(f"[Wellfound] Error: {e}")
    
    return jobs


def scrape_all_indian_boards() -> List[Dict]:
    """
    Scrape Indian job boards for AI/ML/Data/Cloud internships
    Sources: Internshala (reliable), Unstop (API)
    
    Returns:
        Combined list of all jobs
    """
    all_jobs = []
    
    # AI/ML/Data/Cloud domain search terms for Internshala
    ai_ml_terms = [
        "machine-learning",
        "data-science", 
        "artificial-intelligence",
        "python",
        "data-analytics",
        "deep-learning",
        "cloud-computing",
        "devops",
        "data-engineering",
        "mlops",
        "aws",
        "azure",
    ]
    
    # 1. Scrape Internshala (HTML scraping - works well)
    print("[Indian Boards] Scraping Internshala...")
    for term in ai_ml_terms:
        internshala_jobs = scrape_internshala(term, max_results=20)
        all_jobs.extend(internshala_jobs)
        time.sleep(random.uniform(1, 2))
    
    # 2. Scrape Unstop (API - all internships)
    print("\n[Indian Boards] Scraping Unstop...")
    unstop_jobs = scrape_unstop(max_results=50)
    all_jobs.extend(unstop_jobs)
    
    print(f"\n[Indian Boards] Total jobs scraped: {len(all_jobs)}")
    
    # Save results to file
    output_file = "jobs_indian.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_jobs, f, indent=2, ensure_ascii=False)
    print(f"[Indian Boards] Saved {len(all_jobs)} jobs to {output_file}")
    
    return all_jobs


if __name__ == "__main__":
    jobs = scrape_all_indian_boards()
    print(f"[Indian Boards] Completed: {len(jobs)} jobs")
