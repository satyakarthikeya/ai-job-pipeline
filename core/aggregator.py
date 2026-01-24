#!/usr/bin/env python3
"""
Job Aggregator
Merges and deduplicates jobs from multiple sources
"""

import json
import hashlib
from typing import List, Dict
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def normalize_url(url: str) -> str:
    """
    Normalize URL by removing tracking parameters and fragments
    
    Args:
        url: Raw URL
        
    Returns:
        Normalized URL
    """
    try:
        parsed = urlparse(url)
        
        # Remove common tracking parameters
        if parsed.query:
            params = parse_qs(parsed.query)
            # Remove tracking params
            tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 'ref', 'source', 'via']
            cleaned_params = {k: v for k, v in params.items() if k not in tracking_params}
            
            if cleaned_params:
                query = urlencode(cleaned_params, doseq=True)
            else:
                query = ''
        else:
            query = parsed.query
        
        # Reconstruct URL without fragment
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            query,
            ''  # Remove fragment
        ))
        
        return normalized.lower().rstrip('/')
        
    except Exception:
        return url.lower().rstrip('/')


def compute_job_hash(job: Dict) -> str:
    """
    Compute a unique hash for a job based on normalized URL
    
    Args:
        job: Job dictionary
        
    Returns:
        SHA256 hash
    """
    url = job.get('url', '')
    normalized = normalize_url(url)
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def load_jobs_from_file(filepath: str) -> List[Dict]:
    """
    Load jobs from a JSON file
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        List of job dictionaries
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            jobs = json.load(f)
            print(f"[Aggregator] Loaded {len(jobs)} jobs from {filepath}")
            return jobs
    except FileNotFoundError:
        print(f"[Aggregator] File not found: {filepath}")
        return []
    except json.JSONDecodeError:
        print(f"[Aggregator] Invalid JSON in: {filepath}")
        return []
    except Exception as e:
        print(f"[Aggregator] Error loading {filepath}: {e}")
        return []


def merge_jobs(source_files: List[str]) -> List[Dict]:
    """
    Merge jobs from multiple source files and deduplicate
    
    Args:
        source_files: List of JSON file paths
        
    Returns:
        Deduplicated list of jobs
    """
    all_jobs = []
    seen_hashes = set()
    seen_urls = set()
    
    # Load all jobs from all sources
    for filepath in source_files:
        jobs = load_jobs_from_file(filepath)
        
        for job in jobs:
            # Skip jobs without URL
            if not job.get('url'):
                continue
            
            # Compute hash for deduplication
            job_hash = compute_job_hash(job)
            normalized_url = normalize_url(job['url'])
            
            # Check if already seen
            if job_hash in seen_hashes or normalized_url in seen_urls:
                print(f"[Aggregator] Duplicate found: {job.get('title', 'N/A')[:50]}")
                continue
            
            # Add to seen sets
            seen_hashes.add(job_hash)
            seen_urls.add(normalized_url)
            
            # Normalize job fields
            normalized_job = {
                'title': job.get('title', 'N/A'),
                'company': job.get('company', 'Unknown'),
                'location': job.get('location', 'N/A'),
                'url': job.get('url', ''),
                'description': job.get('description', job.get('snippet', 'N/A')),
                'posted_date': job.get('posted_date', 'N/A'),
                'source': job.get('source', 'unknown'),
                'scraped_at': job.get('scraped_at', ''),
                'job_hash': job_hash
            }
            
            all_jobs.append(normalized_job)
    
    print(f"[Aggregator] Total unique jobs after deduplication: {len(all_jobs)}")
    return all_jobs


def save_jobs(jobs: List[Dict], output_file: str):
    """
    Save jobs to JSON file
    
    Args:
        jobs: List of job dictionaries
        output_file: Output file path
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
    print(f"[Aggregator] Saved {len(jobs)} jobs to {output_file}")


if __name__ == "__main__":
    # Example usage
    source_files = [
        'jobs_google.json',
        'jobs_jobspy.json',
        'jobs_ats.json',
        'jobs_reddit.json',
        'jobs_github.json'
    ]
    
    merged_jobs = merge_jobs(source_files)
    save_jobs(merged_jobs, 'jobs_merged.json')
