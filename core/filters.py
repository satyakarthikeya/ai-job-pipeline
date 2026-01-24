#!/usr/bin/env python3
"""
Job Filters
Applies multi-stage filtering for AI/ML internships
"""

import re
from typing import List, Dict


# Keyword sets for filtering
AI_ML_KEYWORDS = [
    'ai', 'artificial intelligence', 'ml', 'machine learning',
    'deep learning', 'neural network', 'nlp', 'natural language processing',
    'computer vision', 'data science', 'llm', 'large language model',
    'transformer', 'pytorch', 'tensorflow', 'scikit-learn',
    'generative ai', 'gpt', 'bert', 'reinforcement learning',
    # Cloud & MLOps keywords
    'mlops', 'ml ops', 'devops', 'cloud', 'aws', 'azure', 'gcp',
    'kubernetes', 'docker', 'data engineer', 'data pipeline',
    'airflow', 'mlflow', 'kubeflow', 'sagemaker', 'vertex ai',
    'ci/cd', 'model deployment', 'ml infrastructure', 'ai infrastructure',
    'data platform', 'analytics', 'big data', 'spark', 'kafka'
]

LOCATION_KEYWORDS = [
    'india', 'remote', 'bangalore', 'bengaluru', 'hyderabad',
    'pune', 'mumbai', 'delhi', 'ncr', 'chennai', 'kolkata',
    'gurugram', 'noida', 'anywhere'
]

INTERNSHIP_KEYWORDS = [
    'intern', 'internship', 'co-op', 'trainee', 'apprentice',
    'summer intern', 'winter intern', 'research intern'
]

# Exclude keywords (full-time positions)
EXCLUDE_KEYWORDS = [
    'senior', 'principal', 'lead', 'manager', 'director',
    '5+ years', '3+ years', 'experienced', 'staff engineer'
]


def calculate_relevance_score(job: Dict) -> int:
    """
    Calculate relevance score for a job (0-100)
    
    Args:
        job: Job dictionary
        
    Returns:
        Relevance score
    """
    score = 0
    text = (job.get('title', '') + ' ' + job.get('description', '')).lower()
    
    # AI/ML keyword matching (max 40 points)
    ai_matches = sum(1 for keyword in AI_ML_KEYWORDS if keyword in text)
    score += min(ai_matches * 5, 40)
    
    # Location matching (max 30 points)
    location_text = job.get('location', '').lower()
    location_matches = sum(1 for keyword in LOCATION_KEYWORDS if keyword in location_text)
    score += min(location_matches * 10, 30)
    
    # Internship keyword matching (max 30 points)
    internship_matches = sum(1 for keyword in INTERNSHIP_KEYWORDS if keyword in text)
    score += min(internship_matches * 15, 30)
    
    # Penalty for exclude keywords
    exclude_matches = sum(1 for keyword in EXCLUDE_KEYWORDS if keyword in text)
    score -= exclude_matches * 10
    
    return max(0, score)


def filter_ai_ml_keywords(jobs: List[Dict]) -> List[Dict]:
    """
    Filter jobs that contain AI/ML keywords
    
    Args:
        jobs: List of job dictionaries
        
    Returns:
        Filtered list
    """
    filtered = []
    
    for job in jobs:
        text = (job.get('title', '') + ' ' + job.get('description', '')).lower()
        
        # Check if any AI/ML keyword is present
        if any(keyword in text for keyword in AI_ML_KEYWORDS):
            filtered.append(job)
    
    print(f"[Filters] AI/ML keyword filter: {len(jobs)} → {len(filtered)}")
    return filtered


def filter_location(jobs: List[Dict]) -> List[Dict]:
    """
    Filter jobs by location (India or Remote)
    More lenient - also checks title/description and allows empty locations
    
    Args:
        jobs: List of job dictionaries
        
    Returns:
        Filtered list
    """
    filtered = []
    
    for job in jobs:
        location = job.get('location', '').lower()
        title = job.get('title', '').lower()
        description = job.get('description', '').lower()
        company = job.get('company', '').lower()
        
        # Combined text to check
        all_text = f"{location} {title} {description} {company}"
        
        # Check if any location keyword is present in any field
        if any(keyword in all_text for keyword in LOCATION_KEYWORDS):
            filtered.append(job)
        # Also allow if location is empty/unknown (assume remote-friendly)
        elif not location or location in ['', 'unknown', 'not specified', 'n/a']:
            filtered.append(job)
    
    print(f"[Filters] Location filter: {len(jobs)} → {len(filtered)}")
    return filtered


def filter_internship(jobs: List[Dict]) -> List[Dict]:
    """
    Filter for internship and entry-level positions
    More lenient - also includes junior, entry-level, associate roles
    
    Args:
        jobs: List of job dictionaries
        
    Returns:
        Filtered list
    """
    # Extended keywords to include more entry-level positions
    entry_level_keywords = INTERNSHIP_KEYWORDS + [
        'junior', 'entry level', 'entry-level', 'associate',
        'graduate', 'fresher', 'new grad', 'early career',
        'beginner', 'starter', 'rotational'
    ]
    
    filtered = []
    
    for job in jobs:
        text = (job.get('title', '') + ' ' + job.get('description', '')).lower()
        
        # Must contain internship/entry-level keyword
        if any(keyword in text for keyword in entry_level_keywords):
            # Should NOT contain exclude keywords (senior roles)
            if not any(exclude in text for exclude in ['senior', 'principal', 'lead', 'staff', 'director']):
                filtered.append(job)
    
    print(f"[Filters] Internship filter: {len(jobs)} → {len(filtered)}")
    return filtered


def filter_experience_level(jobs: List[Dict]) -> List[Dict]:
    """
    Filter jobs for entry-level / low experience requirements
    
    Args:
        jobs: List of job dictionaries
        
    Returns:
        Filtered list
    """
    filtered = []
    
    for job in jobs:
        text = (job.get('title', '') + ' ' + job.get('description', '')).lower()
        
        # Exclude if requires significant experience
        exclude_patterns = [
            r'\d+\+?\s*years?',  # "3+ years", "5 years"
            r'senior', r'principal', r'lead', r'manager'
        ]
        
        if not any(re.search(pattern, text) for pattern in exclude_patterns):
            filtered.append(job)
        elif re.search(r'0-[12]\s*years?', text):  # "0-1 years" is okay
            filtered.append(job)
    
    print(f"[Filters] Experience filter: {len(jobs)} → {len(filtered)}")
    return filtered


def apply_all_filters(jobs: List[Dict], min_score: int = 30) -> List[Dict]:
    """
    Apply all filters and score jobs
    
    Args:
        jobs: List of job dictionaries
        min_score: Minimum relevance score to keep
        
    Returns:
        Filtered and scored list
    """
    print(f"[Filters] Starting with {len(jobs)} jobs")
    
    # Apply filters sequentially
    jobs = filter_ai_ml_keywords(jobs)
    jobs = filter_location(jobs)
    jobs = filter_internship(jobs)
    jobs = filter_experience_level(jobs)
    
    # Calculate scores
    for job in jobs:
        job['relevance_score'] = calculate_relevance_score(job)
    
    # Filter by minimum score
    jobs = [job for job in jobs if job['relevance_score'] >= min_score]
    print(f"[Filters] Score filter (min {min_score}): {len(jobs)} jobs remaining")
    
    # Sort by score (highest first)
    jobs.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    print(f"[Filters] Final count: {len(jobs)} jobs")
    return jobs


if __name__ == "__main__":
    import json
    
    # Example usage
    with open('jobs_merged.json', 'r') as f:
        jobs = json.load(f)
    
    filtered_jobs = apply_all_filters(jobs)
    
    with open('jobs_filtered.json', 'w', encoding='utf-8') as f:
        json.dump(filtered_jobs, f, indent=2, ensure_ascii=False)
    
    print(f"[Filters] Saved filtered jobs to jobs_filtered.json")
