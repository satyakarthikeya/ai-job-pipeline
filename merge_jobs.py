#!/usr/bin/env python3
"""
Merge Jobs - Stage 2 Processor
Aggregates all scraped jobs, filters, checks cache, and sends alerts
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.aggregator import merge_jobs
from core.filters import apply_all_filters
from core.cache_manager import CacheManager
from core.discord_alert import send_discord_alert, send_summary_message


def main():
    print("=" * 60)
    print("AI Job Pipeline - Stage 2: Merge & Alert")
    print("=" * 60)
    
    # Define source files - focused on Indian job boards
    source_files = [
        'jobs_jobspy.json',      # LinkedIn (most reliable)
        'jobs_indian.json',      # Internshala, Unstop, Naukri
        'jobs_google.json',      # Google Jobs
    ]
    
    # Filter to only existing files
    existing_files = [f for f in source_files if os.path.exists(f)]
    print(f"\n[Stage 2] Found {len(existing_files)} source files: {existing_files}")
    
    if not existing_files:
        print("[Stage 2] ⚠️  No source files found. Nothing to process.")
        return
    
    # Step 1: Aggregate and deduplicate
    print("\n[Step 1/4] Aggregating jobs from all sources...")
    all_jobs = merge_jobs(existing_files)
    total_scraped = len(all_jobs)
    
    # Step 2: Apply filters (lowered min_score to 20 for more results)
    print("\n[Step 2/4] Applying AI/ML internship filters...")
    filtered_jobs = apply_all_filters(all_jobs, min_score=20)
    total_filtered = len(filtered_jobs)
    
    # Step 3: Check cache for new jobs
    print("\n[Step 3/4] Checking cache for new jobs...")
    cache_manager = CacheManager('jobs_cache.json')
    new_jobs, cache_stats = cache_manager.process_jobs(filtered_jobs)
    
    # Step 4: Send Discord alerts
    print("\n[Step 4/4] Sending Discord alerts...")
    webhook_url = os.getenv('DISCORD_WEBHOOK')
    notifications_disabled = os.getenv('DISABLE_NOTIFICATIONS', 'false').lower() == 'true'
    
    if notifications_disabled:
        print("[Stage 2] 🔕 DISABLE_NOTIFICATIONS=true. Discord alerts are disabled.")
    elif not webhook_url:
        print("[Stage 2] ⚠️  DISCORD_WEBHOOK not set. Skipping alerts.")
    else:
        if new_jobs:
            success = send_discord_alert(new_jobs, webhook_url)
            if success:
                print(f"[Stage 2] ✅ Sent {len(new_jobs)} job alerts to Discord")
            else:
                print("[Stage 2] ❌ Failed to send Discord alerts")
        else:
            print("[Stage 2] ℹ️  No new jobs to alert")
    
    # Send summary
    summary_stats = {
        'total_scraped': total_scraped,
        'filtered': total_filtered,
        'new_jobs': len(new_jobs),
        'cache_size': cache_stats['cache_size']
    }
    
    if webhook_url and not notifications_disabled:
        send_summary_message(summary_stats, webhook_url)
    
    # Print final summary
    print("\n" + "=" * 60)
    print("Pipeline Summary")
    print("=" * 60)
    print(f"Total Scraped:       {total_scraped}")
    print(f"After Filtering:     {total_filtered}")
    print(f"New Jobs:            {len(new_jobs)}")
    print(f"Already Seen:        {cache_stats['already_seen']}")
    print(f"Cache Size:          {cache_stats['cache_size']} jobs")
    print("=" * 60)
    print("✅ Pipeline completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
