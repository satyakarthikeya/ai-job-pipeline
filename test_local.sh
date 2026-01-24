#!/bin/bash
#
# Local Testing Script
# Tests the entire pipeline locally with your .env file
#

set -e  # Exit on error

echo "============================================================"
echo "AI Job Pipeline - Local Test"
echo "============================================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo ""
    echo "Create a .env file with your Discord webhook:"
    echo "  cp .env.example .env"
    echo "  nano .env  # Edit and add your webhook URL"
    exit 1
fi

# Check if DISCORD_WEBHOOK is set
source .env
if [ -z "$DISCORD_WEBHOOK" ]; then
    echo "⚠️  Warning: DISCORD_WEBHOOK is empty in .env file"
    echo "Discord alerts will be skipped"
    echo ""
fi

echo "Step 1/5: Installing dependencies..."
pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo ""

echo "Step 2/5: Running LinkedIn scraper (via JobSpy)..."
python3 ultimate_scraper.py --source linkedin
echo ""

echo "Step 3/5: Running Indian Job Boards (Internshala, Unstop)..."
python3 ultimate_scraper.py --source indian-boards
echo ""

echo "Step 4/5: Running Google Jobs scraper..."
python3 ultimate_scraper.py --source google-jobs
echo ""

echo "Step 5/5: Merging jobs and sending alerts..."
python3 merge_jobs.py
echo ""

echo "============================================================"
echo "✅ Local test completed!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Check your Discord channel for alerts"
echo "  2. Review jobs_cache.json for stored jobs"
echo "  3. Run 'python3 test_pipeline.py' to verify components"
echo ""
