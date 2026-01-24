#!/usr/bin/env python3
"""
Ultimate Scraper - Stage 1 Orchestrator
Runs individual scrapers based on command-line argument
"""

import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description='Run a specific job scraper')
    parser.add_argument('--source', required=True, 
                       choices=['linkedin', 'indian-boards', 'google-jobs'],
                       help='Which scraper to run')
    
    args = parser.parse_args()
    
    print(f"[Orchestrator] Running scraper: {args.source}")
    
    try:
        if args.source == 'linkedin':
            # LinkedIn via JobSpy (most reliable source)
            from scrapers.jobspy_scraper import scrape_all_jobspy_sources
            scrape_all_jobspy_sources()
        
        elif args.source == 'indian-boards':
            # Internshala + Unstop
            from scrapers.indian_boards import scrape_all_indian_boards
            scrape_all_indian_boards()
            
        elif args.source == 'google-jobs':
            from scrapers.google_jobs import scrape_all_queries
            scrape_all_queries()
        
        print(f"[Orchestrator] ✅ Source '{args.source}' completed successfully")
        
    except Exception as e:
        print(f"[Orchestrator] ❌ Error running '{args.source}': {e}")
        # Don't exit with error code - we want other scrapers to continue
        sys.exit(0)


if __name__ == "__main__":
    main()
