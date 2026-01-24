#!/usr/bin/env python3
"""
Pre-Push Validation Script
Runs quick checks before pushing to GitHub
"""

import sys
import os

def check_files_exist():
    """Check all required files exist"""
    required_files = [
        'ultimate_scraper.py',
        'merge_jobs.py',
        'requirements.txt',
        '.github/workflows/ultimate_scraper.yml',
        'README.md',
        'core/discord_alert.py',
        'core/filters.py',
        'core/aggregator.py',
        'core/cache_manager.py',
        'scrapers/jobspy_scraper.py',
        'scrapers/indian_boards.py',
        'scrapers/google_jobs.py',
    ]
    
    missing = []
    for f in required_files:
        if not os.path.exists(f):
            missing.append(f)
    
    if missing:
        print("❌ Missing files:")
        for f in missing:
            print(f"  - {f}")
        return False
    
    print("✅ All required files present")
    return True


def check_imports():
    """Check if Python modules can be imported"""
    try:
        from core import discord_alert, filters, aggregator, cache_manager
        from scrapers import jobspy_scraper, indian_boards, google_jobs
        import ultimate_scraper
        import merge_jobs
        print("✅ All Python modules importable")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def check_motivational_quotes():
    """Check motivational quotes feature"""
    try:
        from core.discord_alert import MOTIVATIONAL_QUOTES
        if len(MOTIVATIONAL_QUOTES) > 0:
            print(f"✅ Motivational quotes loaded ({len(MOTIVATIONAL_QUOTES)} quotes)")
            print(f"   Sample: {MOTIVATIONAL_QUOTES[0][:60]}...")
            return True
        else:
            print("❌ No motivational quotes found")
            return False
    except Exception as e:
        print(f"❌ Error loading quotes: {e}")
        return False


def check_search_terms():
    """Check search terms are configured"""
    try:
        from scrapers.jobspy_scraper import scrape_all_jobspy_sources
        from scrapers.indian_boards import scrape_all_indian_boards
        print("✅ Search terms configured in scrapers")
        return True
    except Exception as e:
        print(f"❌ Error checking search terms: {e}")
        return False


def check_workflow():
    """Check GitHub Actions workflow"""
    workflow_file = '.github/workflows/ultimate_scraper.yml'
    
    if not os.path.exists(workflow_file):
        print(f"❌ Workflow file not found: {workflow_file}")
        return False
    
    with open(workflow_file, 'r') as f:
        content = f.read()
    
    checks = [
        ('schedule:', 'Scheduled run'),
        ('workflow_dispatch:', 'Manual trigger'),
        ('linkedin', 'LinkedIn scraper'),
        ('indian-boards', 'Indian boards scraper'),
        ('DISCORD_WEBHOOK', 'Discord webhook'),
    ]
    
    for check, desc in checks:
        if check in content:
            print(f"  ✅ {desc}")
        else:
            print(f"  ❌ {desc} not found")
            return False
    
    print("✅ GitHub Actions workflow configured")
    return True


def main():
    print("=" * 60)
    print("AI Job Pipeline - Pre-Push Validation")
    print("=" * 60)
    print()
    
    checks = [
        ("File Structure", check_files_exist),
        ("Python Imports", check_imports),
        ("Motivational Quotes", check_motivational_quotes),
        ("Search Terms", check_search_terms),
        ("GitHub Workflow", check_workflow),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n[{name}]")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append(False)
    
    print()
    print("=" * 60)
    if all(results):
        print("✅ All checks passed! Ready to push to GitHub")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. git add .")
        print("  2. git commit -m 'Your message'")
        print("  3. git push")
        print()
        print("Don't forget to:")
        print("  - Add DISCORD_WEBHOOK secret in GitHub Settings")
        print("  - Enable GitHub Actions in Actions tab")
        return 0
    else:
        print("❌ Some checks failed. Please fix before pushing.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
