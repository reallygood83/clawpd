# BUILD INSTRUCTIONS

Read SPEC.md for the full spec. Build the YouTube PD Agent as an OpenClaw skill.

## Priority Order
1. Create project structure (all folders + files)
2. Build core utilities first (scripts/utils/)
3. Build main modules (scripts/)
4. Create templates + niche presets
5. Write SKILL.md, README.md
6. Commit and push to origin main

## Key Requirements
- Python 3.10+ only, minimal dependencies
- YouTube Data API v3 for channel/video analysis (user provides YOUTUBE_API_KEY)
- web_fetch style HTTP for web scraping (use urllib, no selenium)
- YouTube suggest API for keyword trends (no API key needed)
- All scripts must work standalone AND be callable from OpenClaw
- vidIQ/Grok are OPTIONAL enhancements, core must work without them
- Include niche presets: real_estate.json, tech_ai.json, education.json, custom.json
- PD-level plan output: cue sheet (second-by-second), full script, thumbnail specs, SEO package, shooting guide, competition analysis
- SWOT analysis: YouTube API data comparison + LLM qualitative analysis

## File Structure
```
clawpd/
├── SKILL.md
├── README.md
├── requirements.txt
├── scripts/
│   ├── onboard.py
│   ├── channel_analyzer.py
│   ├── source_collector.py
│   ├── trend_matcher.py
│   ├── plan_generator.py
│   ├── swot_analyzer.py
│   └── utils/
│       ├── youtube_api.py
│       ├── rss_fetcher.py
│       ├── web_scraper.py
│       ├── naver_fetcher.py
│       └── keyword_suggest.py
├── templates/
│   ├── pd_plan.md
│   ├── swot_report.md
│   └── onboard_questions.json
├── presets/
│   ├── real_estate.json
│   ├── tech_ai.json
│   ├── education.json
│   └── custom.json
└── data/
    └── .gitkeep
```

## When done
After all files are created and working:
```bash
git add -A
git commit -m "feat: YouTube PD Agent v1.0 - AI-powered YouTube content planning"
git push origin main
openclaw system event --text "Done: clawpd v1.0 built and pushed to GitHub" --mode now
```
