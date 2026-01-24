#!/usr/bin/env python3
"""
JobSpy Scraper
Uses python-jobspy library to scrape Indeed, LinkedIn, and Glassdoor
"""

import json
from datetime import datetime
from typing import List, Dict

try:
    from jobspy import scrape_jobs
    JOBSPY_AVAILABLE = True
except ImportError:
    print("[JobSpy] Warning: python-jobspy not installed. Install with: pip install python-jobspy")
    JOBSPY_AVAILABLE = False


def scrape_indeed(search_term: str, location: str = "India", results_wanted: int = 50) -> List[Dict]:
    """
    Scrape Indeed using JobSpy
    
    Args:
        search_term: Job search term
        location: Location to search in
        results_wanted: Number of results to fetch
        
    Returns:
        List of job dictionaries
    """
    if not JOBSPY_AVAILABLE:
        return []
    
    try:
        print(f"[JobSpy-Indeed] Searching for '{search_term}' in {location}")
        
        jobs_df = scrape_jobs(
            site_name=["indeed"],
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            hours_old=168,  # Last 7 days
            country_indeed='India',
        )
        
        if jobs_df is None or jobs_df.empty:
            print("[JobSpy-Indeed] No jobs found")
            return []
        
        print(f"[JobSpy-Indeed] Found {len(jobs_df)} jobs")
        
        # Convert DataFrame to list of dicts
        jobs = []
        for _, row in jobs_df.iterrows():
            job = {
                'title': str(row.get('title', '')),
                'company': str(row.get('company', '')),
                'location': str(row.get('location', '')),
                'url': str(row.get('job_url', '')),
                'description': str(row.get('description', ''))[:500],  # Truncate
                'posted_date': str(row.get('date_posted', '')),
                'source': 'indeed',
                'scraped_at': datetime.now().isoformat()
            }
            jobs.append(job)
        
        return jobs
        
    except Exception as e:
        print(f"[JobSpy-Indeed] Error: {e}")
        return []


def scrape_linkedin(search_term: str, location: str = "India", results_wanted: int = 30) -> List[Dict]:
    """
    Scrape LinkedIn using JobSpy
    
    Args:
        search_term: Job search term
        location: Location to search in
        results_wanted: Number of results to fetch
        
    Returns:
        List of job dictionaries
    """
    if not JOBSPY_AVAILABLE:
        return []
    
    try:
        print(f"[JobSpy-LinkedIn] Searching for '{search_term}' in {location}")
        
        jobs_df = scrape_jobs(
            site_name=["linkedin"],
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            hours_old=168,  # Last 7 days
        )
        
        if jobs_df is None or jobs_df.empty:
            print("[JobSpy-LinkedIn] No jobs found")
            return []
        
        print(f"[JobSpy-LinkedIn] Found {len(jobs_df)} jobs")
        
        # Convert DataFrame to list of dicts
        jobs = []
        for _, row in jobs_df.iterrows():
            job = {
                'title': str(row.get('title', '')),
                'company': str(row.get('company', '')),
                'location': str(row.get('location', '')),
                'url': str(row.get('job_url', '')),
                'description': str(row.get('description', ''))[:500],
                'posted_date': str(row.get('date_posted', '')),
                'source': 'linkedin',
                'scraped_at': datetime.now().isoformat()
            }
            jobs.append(job)
        
        return jobs
        
    except Exception as e:
        print(f"[JobSpy-LinkedIn] Error: {e}")
        return []


def scrape_glassdoor(search_term: str, location: str = "India", results_wanted: int = 30) -> List[Dict]:
    """
    Scrape Glassdoor using JobSpy
    
    Args:
        search_term: Job search term
        location: Location to search in
        results_wanted: Number of results to fetch
        
    Returns:
        List of job dictionaries
    """
    if not JOBSPY_AVAILABLE:
        return []
    
    try:
        print(f"[JobSpy-Glassdoor] Searching for '{search_term}' in {location}")
        
        jobs_df = scrape_jobs(
            site_name=["glassdoor"],
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            hours_old=168,  # Last 7 days
        )
        
        if jobs_df is None or jobs_df.empty:
            print("[JobSpy-Glassdoor] No jobs found")
            return []
        
        print(f"[JobSpy-Glassdoor] Found {len(jobs_df)} jobs")
        
        # Convert DataFrame to list of dicts
        jobs = []
        for _, row in jobs_df.iterrows():
            job = {
                'title': str(row.get('title', '')),
                'company': str(row.get('company', '')),
                'location': str(row.get('location', '')),
                'url': str(row.get('job_url', '')),
                'description': str(row.get('description', ''))[:500],
                'posted_date': str(row.get('date_posted', '')),
                'source': 'glassdoor',
                'scraped_at': datetime.now().isoformat()
            }
            jobs.append(job)
        
        return jobs
        
    except Exception as e:
        print(f"[JobSpy-Glassdoor] Error: {e}")
        return []


def scrape_all_jobspy_sources() -> List[Dict]:
    """
    Scrape all JobSpy sources with multiple search terms
    
    Returns:
        Combined list of all jobs
    """
    all_jobs = []
    
    # Search terms - AI/ML/Cloud/MLOps
    search_terms = [
        "AI Intern",
        "Machine Learning Intern",
        "Data Science Intern",
        "MLOps Intern",
        "Data Engineer Intern",
        "Cloud Engineer Intern",
        "DevOps Intern",
    ]
    
    for term in search_terms:
        # Indeed (no rate limit, can be aggressive)
        indeed_jobs = scrape_indeed(term, results_wanted=40)
        all_jobs.extend(indeed_jobs)
        
        # LinkedIn (be conservative)
        linkedin_jobs = scrape_linkedin(term, results_wanted=20)
        all_jobs.extend(linkedin_jobs)
        
        # Glassdoor (optional, can be flaky)
        glassdoor_jobs = scrape_glassdoor(term, results_wanted=15)
        all_jobs.extend(glassdoor_jobs)
    
    print(f"[JobSpy] Total jobs scraped: {len(all_jobs)}")
    
    # Save results to file
    output_file = "jobs_jobspy.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_jobs, f, indent=2, ensure_ascii=False)
    print(f"[JobSpy] Saved {len(all_jobs)} jobs to {output_file}")
    
    return all_jobs


if __name__ == "__main__":
    # Run scraper
    jobs = scrape_all_jobspy_sources()
    print(f"[JobSpy] Completed: {len(jobs)} jobs")
