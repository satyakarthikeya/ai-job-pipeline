# AI/ML Job Pipeline 🤖

![Python](https://img.shields.io/badge/python-3.10+-blue)
![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-green)
![Cost](https://img.shields.io/badge/cost-%240%2Fmonth-brightgreen)
![License](https://img.shields.io/badge/license-MIT-orange)

**Automated AI/ML/Cloud internship aggregation system that runs 100% free on GitHub Actions**

Scrapes 250+ job postings daily from LinkedIn, Internshala, Unstop, and more. Filters for AI, ML, Data Science, MLOps, Cloud, and DevOps internships in India. Sends Discord alerts with motivational quotes when jobs are found (or not found).

---

## ✨ Features

- 🌐 **Multi-Source Scraping**: LinkedIn (via JobSpy), Internshala, Unstop, Google Jobs
- 🎯 **Smart AI/ML/Cloud Filtering**: AI, ML, Data Science, MLOps, DevOps, Cloud (AWS/Azure/GCP)
- 💾 **Duplicate Detection**: Deduplicates across sources using title + company matching
- 🚀 **Parallel Scraping**: GitHub Actions matrix strategy for speed
- 💬 **Discord Alerts**: Rich embeds with company, location, apply links
- 💪 **Motivational Quotes**: Random inspirational quotes when no jobs found
- 💰 **$0/month**: Runs entirely on GitHub Actions free tier
- 🔄 **Daily Updates**: Runs automatically at 9 AM UTC (2:30 PM IST)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1: PARALLEL SCRAPING (3 jobs simultaneously)         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  LinkedIn    │  │ Internshala  │  │ Google Jobs  │      │
│  │  (JobSpy)    │  │  + Unstop    │  │  (backup)    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         └──────────────────┼──────────────────┘             │
│                            ▼                                │
│                    Upload as Artifacts                      │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 2: MERGE & ALERT                                     │
│                                                             │
│  Download → Merge → Filter → Cache Check → Discord Alert   │
│                                   │                         │
│                                   ▼                         │
│                          Update jobs_cache.json             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Fork this Repository

Click the **Fork** button at the top right.

### 2. Set up Discord Webhook

1. Go to your Discord server settings
2. Navigate to **Integrations → Webhooks**
3. Click **New Webhook**
4. Copy the webhook URL

### 3. Add GitHub Secret

1. Go to your forked repo → **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `DISCORD_WEBHOOK`
4. Value: Paste your webhook URL
5. Click **Add secret**

### 4. Enable GitHub Actions

1. Go to **Actions** tab
2. Click **"I understand my workflows, go ahead and enable them"**

### 5. Test Manually (Optional)

1. Go to **Actions → AI Job Pipeline**
2. Click **Run workflow → Run workflow**
3. Check Discord for alerts!

---

## 📁 Project Structure

```
ai-job-pipeline/
├── .github/workflows/
│   └── ultimate_scraper.yml    # GitHub Actions workflow
├── core/
│   ├── aggregator.py            # Job deduplication
│   ├── filters.py               # AI/ML/Cloud keyword filtering
│   ├── cache_manager.py         # Duplicate job detection
│   └── discord_alert.py         # Discord notifications
├── scrapers/
│   ├── jobspy_scraper.py        # LinkedIn scraper
│   ├── indian_boards.py         # Internshala + Unstop
│   └── google_jobs.py           # Google Jobs (backup)
├── ultimate_scraper.py          # Orchestrator
├── merge_jobs.py                # Stage 2 processor
├── test_local.sh                # Local testing script
└── requirements.txt             # Python dependencies
```

---

## 🔧 Local Testing

### Prerequisites

- Python 3.10+
- Discord webhook URL

### Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ai-job-pipeline.git
cd ai-job-pipeline

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
nano .env  # Add your DISCORD_WEBHOOK

# Run test
bash test_local.sh
```

### Expected Output

```
✅ Dependencies installed

Step 2/5: Running LinkedIn scraper (via JobSpy)...
[LinkedIn] Found 109 jobs

Step 3/5: Running Indian Job Boards (Internshala, Unstop)...
[Internshala] Found 261 jobs

Step 4/5: Running Google Jobs scraper...
[Google Jobs] Found 0 jobs

Step 5/5: Merging jobs and sending alerts...
Total Scraped:       292
After Filtering:     26
New Jobs:            26
✅ Pipeline completed successfully!
```

---

## 🎯 What Jobs Are Found?

The pipeline searches for internships in:

### Core AI/ML
- Machine Learning
- Deep Learning
- Natural Language Processing (NLP)
- Computer Vision
- AI Research
- Data Science
- Data Analytics

### MLOps & Infrastructure
- MLOps Engineer
- ML Infrastructure
- Model Deployment
- CI/CD for ML
- MLflow, Kubeflow, Airflow

### Cloud & DevOps
- Cloud Engineer (AWS, Azure, GCP)
- DevOps Engineer
- Data Engineer
- Kubernetes, Docker
- Infrastructure as Code

### Location
- India (all cities)
- Remote positions

---

## 📊 Filter Settings

Jobs are scored 0-100 based on:

| Criteria | Max Points |
|----------|-----------|
| AI/ML/Cloud keywords | 40 |
| Location match (India/Remote) | 30 |
| Internship keywords | 30 |

**Minimum score to pass**: 20/100

Jobs are excluded if they contain: `senior`, `principal`, `lead`, `staff`, `director`

---

## 🔔 Discord Alert Format

### When Jobs Are Found

```
🎯 Machine Learning Intern
🏢 Company: DeepMind India
📍 Location: Bangalore
🔍 Source: LinkedIn
🔗 [Apply Now](https://example.com/apply)

Relevance Score: 85/100
```

### When No Jobs Found

```
🔍 No New Jobs Found Today

Don't worry! We're still searching for you.

"Keep pushing forward! The right opportunity 
is just around the corner. 💪"

Total Jobs Checked: 292
Next Check: Tomorrow at 9 AM UTC

💡 Tip: Keep building projects and learning new skills!
```

---

## ⚙️ Customization

### Change Schedule

Edit `.github/workflows/ultimate_scraper.yml`:

```yaml
on:
  schedule:
    - cron: '0 9 * * *'  # 9 AM UTC = 2:30 PM IST
```

[Cron schedule generator](https://crontab.guru/)

### Add More Search Terms

Edit `scrapers/jobspy_scraper.py`:

```python
search_terms = [
    "AI Intern",
    "Machine Learning Intern",
    "Your Custom Term",  # Add here
]
```

Edit `scrapers/indian_boards.py`:

```python
ai_ml_terms = [
    "machine-learning",
    "your-custom-term",  # Add here
]
```

### Adjust Filters

Edit `core/filters.py`:

```python
# Change minimum score (default: 20)
filtered_jobs = apply_all_filters(all_jobs, min_score=15)
```

---

## 🐛 Troubleshooting

### No Discord Alerts

1. Check if `DISCORD_WEBHOOK` secret is set correctly
2. Verify webhook URL is valid (test in Discord settings)
3. Check GitHub Actions logs for errors

### No Jobs Found

- Normal! Some days have fewer jobs
- Check if filters are too strict (lower `min_score`)
- Verify scrapers are running (check Actions logs)

### Workflow Fails

1. Go to **Actions** tab
2. Click on failed run
3. Check logs for error messages
4. Common issues:
   - Rate limiting (scrapers wait automatically)
   - Website structure changed (update selectors)
   - Network timeout (will retry next run)

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| **Sources** | 3 active |
| **Daily Jobs Scraped** | 250-350 |
| **After Filtering** | 20-30 |
| **Runtime** | ~5 minutes |
| **Cost** | $0/month |
| **Runs Per Day** | 1 (configurable) |

---

## 🤝 Contributing

Contributions welcome! Feel free to:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

### Ideas for Contribution

- Add more job sources (Naukri API, WellFound, etc.)
- Improve keyword matching
- Add Telegram/Slack notifications
- Add ML-based job relevance scoring
- Build a web dashboard

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- [JobSpy](https://github.com/Bunsly/JobSpy) - LinkedIn/Indeed scraping
- [Internshala](https://internshala.com) - Indian internship platform
- [Unstop](https://unstop.com) - Student opportunities platform
- GitHub Actions - Free CI/CD

---

## 📧 Contact

Found this helpful? Give it a ⭐ on GitHub!

Have questions? Open an issue or reach out:
- GitHub Issues: [Create Issue](https://github.com/YOUR_USERNAME/ai-job-pipeline/issues)

---

**Happy Job Hunting! 🚀**

*Last Updated: January 2026*
