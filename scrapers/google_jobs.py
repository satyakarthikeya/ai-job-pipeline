#!/usr/bin/env python3
"""
Google for Jobs Scraper
Scrapes Google's job search aggregator for AI/ML internships
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict

# User agent rotation for anti-detection
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
]

# Search queries for AI/ML internships
SEARCH_QUERIES = [
    "AI Intern India",
    "Machine Learning Intern India",
    "Data Science Intern India",
    "NLP Intern India",
    "Deep Learning Intern India",
]


def scrape_google_jobs(query: str, max_results: int = 20) -> List[Dict]:
    """
    Scrape Google for Jobs for a specific query
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of job dictionaries
    """
    jobs = []
    
    # Construct Google for Jobs URL
    base_url = "https://www.google.com/search"
    params = {
        'q': query,
        'ibp': 'htl;jobs',
        'hl': 'en',
    }
    
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        print(f"[Google Jobs] Searching for: {query}")
        response = requests.get(base_url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Google for Jobs uses complex div structures
        # Look for job listing divs (this may need adjustment based on Google's current structure)
        job_cards = soup.find_all('div', class_='PwjeAc')
        
        if not job_cards:
            # Fallback: try different selectors
            job_cards = soup.find_all('li', class_='iFjolb')
        
        print(f"[Google Jobs] Found {len(job_cards)} job cards")
        
        for card in job_cards[:max_results]:
            try:
                job = extract_job_from_card(card)
                if job:
                    job['source'] = 'google_jobs'
                    job['scraped_at'] = datetime.now().isoformat()
                    jobs.append(job)
            except Exception as e:
                print(f"[Google Jobs] Error parsing card: {e}")
                continue
                
    except requests.exceptions.RequestException as e:
        print(f"[Google Jobs] Request error for query '{query}': {e}")
    except Exception as e:
        print(f"[Google Jobs] Unexpected error for query '{query}': {e}")
    
    return jobs


def extract_job_from_card(card) -> Dict:
    """
    Extract job details from a Google job card
    
    Args:
        card: BeautifulSoup element representing a job card
        
    Returns:
        Dictionary with job details or None
    """
    job = {}
    
    # Try to extract title
    title_elem = card.find('div', class_='BjJfJf')
    if not title_elem:
        title_elem = card.find('h2')
    if title_elem:
        job['title'] = title_elem.get_text(strip=True)
    
    # Extract company
    company_elem = card.find('div', class_='vNEEBe')
    if company_elem:
        job['company'] = company_elem.get_text(strip=True)
    
    # Extract location
    location_elem = card.find('div', class_='Qk80Jf')
    if location_elem:
        job['location'] = location_elem.get_text(strip=True)
    
    # Extract URL
    link_elem = card.find('a', href=True)
    if link_elem:
        job['url'] = link_elem['href']
        if job['url'].startswith('/'):
            job['url'] = 'https://www.google.com' + job['url']
    
    # Extract posting date (if available)
    date_elem = card.find('span', class_='LL4CDc')
    if date_elem:
        job['posted_date'] = date_elem.get_text(strip=True)
    
    # Only return if we have at least title and URL
    if 'title' in job and 'url' in job:
        return job
    
    return None


def scrape_all_queries(max_per_query: int = 15) -> List[Dict]:
    """
    Scrape all predefined queries and aggregate results
    
    Args:
        max_per_query: Maximum results per query
        
    Returns:
        Combined list of all jobs
    """
    all_jobs = []
    
    for i, query in enumerate(SEARCH_QUERIES):
        jobs = scrape_google_jobs(query, max_results=max_per_query)
        all_jobs.extend(jobs)
        
        print(f"[Google Jobs] Query {i+1}/{len(SEARCH_QUERIES)}: Found {len(jobs)} jobs")
        
        # Rate limiting: wait 5-8 seconds between queries
        if i < len(SEARCH_QUERIES) - 1:
            wait_time = random.uniform(5, 8)
            print(f"[Google Jobs] Waiting {wait_time:.1f}s before next query...")
            time.sleep(wait_time)
    
    print(f"[Google Jobs] Total jobs scraped: {len(all_jobs)}")
    
    # Save results to file
    output_file = "jobs_google.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_jobs, f, indent=2, ensure_ascii=False)
    print(f"[Google Jobs] Saved {len(all_jobs)} jobs to {output_file}")
    
    return all_jobs


if __name__ == "__main__":
    # Run scraper
    jobs = scrape_all_queries()
    print(f"[Google Jobs] Completed: {len(jobs)} jobs")
