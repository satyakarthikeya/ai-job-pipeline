#!/usr/bin/env python3
"""
Discord Alert
Sends rich Discord embeds for new job postings
"""

import os
import requests
import random
from typing import List, Dict
from datetime import datetime

# Load environment variables from .env file (for local testing)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, will use system env vars


# Motivational quotes for when no jobs are found
MOTIVATIONAL_QUOTES = [
    "Keep pushing forward! The right opportunity is just around the corner. 💪",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill 🌟",
    "Don't watch the clock; do what it does. Keep going. - Sam Levenson ⏰",
    "The only way to do great work is to love what you do. - Steve Jobs ❤️",
    "Opportunities don't happen. You create them. - Chris Grosser 🚀",
    "Your limitation—it's only your imagination. Keep learning, keep growing! 📚",
    "Great things never come from comfort zones. Keep applying! 🎯",
    "Dream it. Wish it. Do it. Your breakthrough is coming! ✨",
    "The harder you work for something, the greater you'll feel when you achieve it. 💼",
    "Success doesn't just find you. You have to go out and get it! 🔥",
    "Don't stop when you're tired. Stop when you're done. 🏃",
    "Every expert was once a beginner. Keep upskilling! 🌱",
    "The best time to plant a tree was 20 years ago. The second best time is now. - Chinese Proverb 🌳",
    "Believe you can and you're halfway there. - Theodore Roosevelt 💫",
    "Your next job is looking for you too. Keep the faith! 🙏"
]


# Color coding by source
SOURCE_COLORS = {
    'google_jobs': 0x4285F4,      # Google Blue
    'indeed': 0x2164F3,            # Indeed Blue
    'linkedin': 0x0077B5,          # LinkedIn Blue
    'glassdoor': 0x0CAA41,         # Glassdoor Green
    'ats_direct_lever': 0xFF6B35,  # Orange
    'ats_direct_greenhouse': 0x66BB6A,  # Green
    'ats_direct_workable': 0x5E44FF,    # Purple
    'ats_direct_ashby': 0x00C7B7,       # Teal
    'reddit': 0xFF4500,            # Reddit Orange
    'github_jobs': 0x181717,       # GitHub Black
    'default': 0x7289DA             # Discord Blurple
}


def get_source_display_name(source: str) -> str:
    """
    Get human-readable source name
    
    Args:
        source: Source identifier
        
    Returns:
        Display name
    """
    mapping = {
        'google_jobs': 'Google for Jobs',
        'indeed': 'Indeed',
        'linkedin': 'LinkedIn',
        'glassdoor': 'Glassdoor',
        'ats_direct_lever': 'Lever',
        'ats_direct_greenhouse': 'Greenhouse',
        'ats_direct_workable': 'Workable',
        'ats_direct_ashby': 'Ashby',
        'reddit': 'Reddit',
        'github_jobs': 'GitHub Jobs'
    }
    return mapping.get(source, source.replace('_', ' ').title())


def create_job_embed(job: Dict) -> Dict:
    """
    Create Discord embed for a job posting
    
    Args:
        job: Job dictionary
        
    Returns:
        Discord embed dictionary
    """
    source = job.get('source', 'unknown')
    color = SOURCE_COLORS.get(source, SOURCE_COLORS['default'])
    
    embed = {
        'title': job.get('title', 'Job Opening')[:256],  # Discord limit
        'url': job.get('url', ''),
        'color': color,
        'fields': [
            {
                'name': '🏢 Company',
                'value': job.get('company', 'Unknown')[:1024],
                'inline': True
            },
            {
                'name': '📍 Location',
                'value': job.get('location', 'N/A')[:1024],
                'inline': True
            },
            {
                'name': '🔍 Source',
                'value': get_source_display_name(source),
                'inline': True
            },
        ],
        'timestamp': datetime.now().isoformat(),
        'footer': {
            'text': f"Relevance Score: {job.get('relevance_score', 0)}/100"
        }
    }
    
    # Add description if available (truncate to fit Discord limits)
    description = job.get('description', '')
    if description and description != 'N/A':
        description = description[:500] + ('...' if len(description) > 500 else '')
        embed['description'] = description
    
    # Add posted date if available
    posted_date = job.get('posted_date', '')
    if posted_date and posted_date != 'N/A':
        embed['fields'].append({
            'name': '📅 Posted',
            'value': posted_date[:1024],
            'inline': True
        })
    
    return embed


def send_discord_alert(jobs: List[Dict], webhook_url: str = None) -> bool:
    """
    Send Discord webhook with job embeds
    
    Args:
        jobs: List of job dictionaries
        webhook_url: Discord webhook URL
        
    Returns:
        True if successful
    """
    if not webhook_url:
        webhook_url = os.getenv('DISCORD_WEBHOOK')
    
    if not webhook_url:
        print("[Discord] No webhook URL provided")
        return False
    
    if not jobs:
        print("[Discord] No jobs to alert")
        return True
    
    print(f"[Discord] Sending alerts for {len(jobs)} jobs")
    
    # Discord allows max 10 embeds per message
    batch_size = 10
    
    for i in range(0, len(jobs), batch_size):
        batch = jobs[i:i+batch_size]
        embeds = [create_job_embed(job) for job in batch]
        
        payload = {
            'username': 'AI Job Scout',
            'avatar_url': 'https://cdn-icons-png.flaticon.com/512/4305/4305093.png',
            'embeds': embeds
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            print(f"[Discord] Sent batch {i//batch_size + 1}/{(len(jobs)-1)//batch_size + 1}")
            
            # Rate limiting: Discord allows 30 requests per minute
            if i + batch_size < len(jobs):
                import time
                time.sleep(2)  # Wait 2 seconds between batches
                
        except requests.exceptions.HTTPError as e:
            print(f"[Discord] HTTP Error: {e}")
            print(f"[Discord] Response: {e.response.text if e.response else 'N/A'}")
            return False
        except Exception as e:
            print(f"[Discord] Error sending alert: {e}")
            return False
    
    print(f"[Discord] Successfully sent {len(jobs)} job alerts")
    return True


def send_summary_message(stats: Dict, webhook_url: str = None):
    """
    Send a summary message with pipeline statistics
    If no new jobs, send a motivational quote
    
    Args:
        stats: Statistics dictionary
        webhook_url: Discord webhook URL
    """
    if not webhook_url:
        webhook_url = os.getenv('DISCORD_WEBHOOK')
    
    if not webhook_url:
        return
    
    new_jobs = stats.get('new_jobs', 0)
    
    # If no new jobs, send motivational quote
    if new_jobs == 0:
        quote = random.choice(MOTIVATIONAL_QUOTES)
        embed = {
            'title': '🔍 No New Jobs Found Today',
            'description': f"Don't worry! We're still searching for you.\n\n**{quote}**",
            'color': 0xFFA500,  # Orange
            'fields': [
                {
                    'name': 'Total Jobs Checked',
                    'value': str(stats.get('total_scraped', 0)),
                    'inline': True
                },
                {
                    'name': 'Next Check',
                    'value': 'Tomorrow at 9 AM UTC',
                    'inline': True
                }
            ],
            'timestamp': datetime.now().isoformat(),
            'footer': {
                'text': '💡 Tip: Keep building projects and learning new skills!'
            }
        }
    else:
        # Normal summary with new jobs
        embed = {
            'title': '📊 Job Pipeline Summary',
            'color': 0x00D9FF,
            'fields': [
                {
                    'name': 'Total Scraped',
                    'value': str(stats.get('total_scraped', 0)),
                    'inline': True
                },
                {
                    'name': 'After Filtering',
                    'value': str(stats.get('filtered', 0)),
                    'inline': True
                },
                {
                    'name': 'New Jobs',
                    'value': str(stats.get('new_jobs', 0)),
                    'inline': True
                },
                {
                    'name': 'Cache Size',
                    'value': str(stats.get('cache_size', 0)),
                    'inline': True
                },
            ],
            'timestamp': datetime.now().isoformat(),
            'footer': {
                'text': '✅ Pipeline completed successfully'
            }
        }
    
    payload = {
        'username': 'AI Job Scout',
        'embeds': [embed]
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        print("[Discord] Sent summary message")
    except Exception as e:
        print(f"[Discord] Error sending summary: {e}")


if __name__ == "__main__":
    # Example usage
    sample_jobs = [
        {
            'title': 'AI Research Intern',
            'company': 'OpenAI',
            'location': 'Remote',
            'url': 'https://example.com/job1',
            'description': 'Work on cutting-edge AI research...',
            'source': 'google_jobs',
            'relevance_score': 85
        }
    ]
    
    # Test (will fail without webhook URL)
    send_discord_alert(sample_jobs)
