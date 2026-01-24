#!/usr/bin/env python3
"""
Cache Manager
Manages 7-day rolling window cache for job tracking
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Tuple


class CacheManager:
    """Manages job cache with 7-day rolling window"""
    
    def __init__(self, cache_file: str = 'jobs_cache.json'):
        """
        Initialize cache manager
        
        Args:
            cache_file: Path to cache JSON file
        """
        self.cache_file = cache_file
        self.cache = self.load_cache()
    
    def load_cache(self) -> Dict:
        """Load cache from disk"""
        if not os.path.exists(self.cache_file):
            return {
                'seen_jobs': {},
                'stats': {
                    'total_jobs_tracked': 0,
                    'cache_size_kb': 0.0,
                    'oldest_job_date': None,
                    'last_cleanup': None,
                    'sources_breakdown': {}
                }
            }
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                print(f"[Cache] Loaded cache with {len(cache.get('seen_jobs', {}))} jobs")
                return cache
        except Exception as e:
            print(f"[Cache] Error loading cache: {e}")
            return {'seen_jobs': {}, 'stats': {}}
    
    def save_cache(self):
        """Save cache to disk"""
        try:
            # Update stats
            self.cache['stats']['total_jobs_tracked'] = len(self.cache['seen_jobs'])
            
            # Calculate cache size
            cache_json = json.dumps(self.cache, indent=2)
            self.cache['stats']['cache_size_kb'] = len(cache_json.encode('utf-8')) / 1024
            
            # Save to file
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                f.write(cache_json)
            
            print(f"[Cache] Saved cache: {self.cache['stats']['total_jobs_tracked']} jobs, "
                  f"{self.cache['stats']['cache_size_kb']:.2f} KB")
        
        except Exception as e:
            print(f"[Cache] Error saving cache: {e}")
    
    def cleanup_old_jobs(self, max_age_days: int = 7):
        """
        Remove jobs older than max_age_days
        
        Args:
            max_age_days: Maximum age in days
        """
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        cutoff_str = cutoff_date.strftime('%Y-%m-%d')
        
        before_count = len(self.cache['seen_jobs'])
        
        # Filter out old jobs
        self.cache['seen_jobs'] = {
            url: info for url, info in self.cache['seen_jobs'].items()
            if info.get('last_seen', '9999-12-31') >= cutoff_str
        }
        
        after_count = len(self.cache['seen_jobs'])
        removed = before_count - after_count
        
        if removed > 0:
            print(f"[Cache] Cleaned up {removed} jobs older than {max_age_days} days")
        
        self.cache['stats']['last_cleanup'] = datetime.now().isoformat()
    
    def is_new_job(self, job: Dict) -> bool:
        """
        Check if a job is new (not seen in last 7 days)
        
        Args:
            job: Job dictionary with 'url' field
            
        Returns:
            True if new, False if already seen
        """
        url = job.get('url', '')
        if not url:
            return False
        
        # Check if URL exists in cache
        if url in self.cache['seen_jobs']:
            job_info = self.cache['seen_jobs'][url]
            
            # Update last_seen date
            job_info['last_seen'] = datetime.now().strftime('%Y-%m-%d')
            
            # Check if we should re-alert (if last alert was >7 days ago and alert_count < 2)
            if job_info.get('alert_count', 0) < 2:
                last_seen = datetime.strptime(job_info['first_seen'], '%Y-%m-%d')
                days_since_first = (datetime.now() - last_seen).days
                
                if days_since_first >= 7:
                    print(f"[Cache] Re-alerting job (still active after 7 days): {job.get('title', 'N/A')[:50]}")
                    job_info['alert_count'] = job_info.get('alert_count', 0) + 1
                    return True
            
            return False
        
        return True
    
    def add_job(self, job: Dict):
        """
        Add a job to the cache
        
        Args:
            job: Job dictionary
        """
        url = job.get('url', '')
        if not url:
            return
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        self.cache['seen_jobs'][url] = {
            'first_seen': today,
            'last_seen': today,
            'alert_count': 1,
            'source': job.get('source', 'unknown'),
            'company': job.get('company', 'Unknown'),
            'title': job.get('title', 'N/A')
        }
        
        # Update source breakdown
        source = job.get('source', 'unknown')
        if 'sources_breakdown' not in self.cache['stats']:
            self.cache['stats']['sources_breakdown'] = {}
        
        self.cache['stats']['sources_breakdown'][source] = \
            self.cache['stats']['sources_breakdown'].get(source, 0) + 1
    
    def process_jobs(self, jobs: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Process jobs through cache and return new jobs
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            Tuple of (new_jobs, statistics)
        """
        print(f"[Cache] Processing {len(jobs)} jobs")
        
        # Cleanup old jobs first
        self.cleanup_old_jobs(max_age_days=7)
        
        new_jobs = []
        
        for job in jobs:
            if self.is_new_job(job):
                self.add_job(job)
                new_jobs.append(job)
        
        # Save cache
        self.save_cache()
        
        stats = {
            'total_processed': len(jobs),
            'new_jobs': len(new_jobs),
            'already_seen': len(jobs) - len(new_jobs),
            'cache_size': len(self.cache['seen_jobs'])
        }
        
        print(f"[Cache] Found {len(new_jobs)} new jobs out of {len(jobs)}")
        
        return new_jobs, stats


if __name__ == "__main__":
    # Example usage
    cm = CacheManager()
    
    # Test with sample jobs
    sample_jobs = [
        {'url': 'https://example.com/job1', 'title': 'AI Intern', 'company': 'Test Corp'},
        {'url': 'https://example.com/job2', 'title': 'ML Intern', 'company': 'Tech Inc'},
    ]
    
    new_jobs, stats = cm.process_jobs(sample_jobs)
    print(f"New jobs: {len(new_jobs)}")
    print(f"Stats: {stats}")
