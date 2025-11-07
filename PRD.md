Product Requirements Document: NGPF Readability Analyzer
Product Overview
Product Name: NGPF Article Readability Analyzer
Purpose: Internal tool to analyze readability of all articles currently linked in NGPF curriculum, establishing a baseline for comparison with future simplified versions.
Core Workflow:

Paste list of article URLs from curriculum
System extracts text from each URL
Calculate readability scores for each article
Export results for baseline tracking
Later: compare with rewritten versions

MVP Features (Must Have)
F1: Bulk URL Input & Processing

Large text area accepting multiple URLs (one per line)
Support for 100+ URLs in a single batch
URL validation with immediate feedback
"Analyze All" button to start processing
Real-time progress indicator: "Processing 23 of 87 articles..."

F2: Text Extraction from URLs

Trafilatura for reliable article extraction (95.8% accuracy)
Clean extraction removing ads, navigation, footers
Fallback to Readability if Trafilatura fails
Error handling for failed extractions
No JavaScript rendering needed (confirmed by you)

F3: Readability Analysis
Calculate for each article:

Flesch-Kincaid Grade Level (primary metric)
SMOG Index (education-focused)
Coleman-Liau Index
Automated Readability Index
Consensus Grade Level (average)
Word count and sentence statistics

F4: Results Display & Export

Table view with columns:

URL (truncated for display)
Article Title (if extracted)
FK Grade | SMOG | Coleman-Liau | ARI | Consensus
Word Count
Status (✓ success, ✗ failed)


CSV Export with all data for spreadsheet analysis
Summary statistics: Average grade level across all articles
Failed URLs listed separately for manual review

Technical Specifications
Tech Stack
Backend (Python):
python# Core libraries
FastAPI          # API framework
Trafilatura      # Primary text extraction (pip install trafilatura)
readability-lxml # Fallback extractor
textstat        # Readability calculations
aiohttp         # Async URL fetching
pandas          # CSV generation
Frontend (Simple React):
javascript// Minimal dependencies
React + TypeScript
Axios for API calls  
Tailwind CSS
PapaParse for CSV handling
API Endpoints
pythonPOST /api/analyze-urls
{
  "urls": [
    "https://example.com/article1",
    "https://example.com/article2"
  ]
}

Response:
{
  "results": [
    {
      "url": "https://example.com/article1",
      "title": "Article Title",
      "extraction_success": true,
      "metrics": {
        "flesch_kincaid_grade": 10.3,
        "smog": 11.2,
        "coleman_liau": 10.8,
        "ari": 10.5,
        "consensus": 10.7
      },
      "statistics": {
        "word_count": 847,
        "sentence_count": 42
      }
    }
  ],
  "summary": {
    "total_urls": 87,
    "successful": 84,
    "failed": 3,
    "average_grade_level": 10.8
  }
}
Simple Implementation
python# main.py
from fastapi import FastAPI
from trafilatura import fetch_url, extract
import textstat
import asyncio
import aiohttp

app = FastAPI()

async def process_url(session, url):
    try:
        # Fetch and extract with Trafilatura
        downloaded = await fetch_url_async(url)
        text = extract(downloaded, include_comments=False, 
                      include_tables=False, no_fallback=False)
        
        if not text:
            return {"url": url, "extraction_success": False}
        
        # Calculate readability metrics
        metrics = {
            'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
            'smog': textstat.smog_index(text),
            'coleman_liau': textstat.coleman_liau_index(text),
            'ari': textstat.automated_readability_index(text)
        }
        metrics['consensus'] = sum(metrics.values()) / len(metrics)
        
        return {
            "url": url,
            "extraction_success": True,
            "text_preview": text[:200],
            "metrics": metrics,
            "statistics": {
                "word_count": textstat.lexicon_count(text),
                "sentence_count": textstat.sentence_count(text)
            }
        }
    except Exception as e:
        return {"url": url, "extraction_success": False, "error": str(e)}

@app.post("/api/analyze-urls")
async def analyze_urls(urls: list[str]):
    async with aiohttp.ClientSession() as session:
        tasks = [process_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    
    successful = [r for r in results if r.get("extraction_success")]
    
    if successful:
        avg_grade = sum(r["metrics"]["flesch_kincaid_grade"] 
                       for r in successful) / len(successful)
    else:
        avg_grade = None
    
    return {
        "results": results,
        "summary": {
            "total_urls": len(urls),
            "successful": len(successful),
            "failed": len(results) - len(successful),
            "average_grade_level": round(avg_grade, 1) if avg_grade else None
        }
    }
```

### User Interface
```
┌────────────────────────────────────────────────────────┐
│  NGPF Article Readability Analyzer                     │
│                                                         │
│  Paste Article URLs (one per line):                    │
│  ┌──────────────────────────────────────────────┐     │
│  │ https://www.nytimes.com/article1...          │     │
│  │ https://www.wsj.com/article2...              │     │
│  │ https://www.bloomberg.com/article3...        │     │
│  │                                               │     │
│  └──────────────────────────────────────────────┘     │
│  87 valid URLs detected                                │
│                                                         │
│  [Analyze All Articles]                                │
│                                                         │
│  ⏳ Processing 23 of 87 articles...                    │
│                                                         │
│  Results:                                              │
│  ┌─────────────────────────────────────────────────┐  │
│  │ Average Grade Level: 10.8 (High School)       │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  │ URL           │ FK  │SMOG│ CL │ARI│Consensus│  │
│  │ nytimes.../a1 │10.3 │11.2│10.8│9.9│ 10.6    │  │
│  │ wsj.com/a2    │12.1 │12.8│11.9│12.│ 12.2    │  │
│  │ bloomberg...  │ 9.8 │10.1│ 9.5│9.2│  9.7    │  │
│                                                     │
│  [Export to CSV]                                   │
└────────────────────────────────────────────────────────┘
Implementation Timeline
Day 1-2: Backend Core

Set up FastAPI with Trafilatura
Create URL processing pipeline
Test with 10-20 NGPF article URLs
Handle edge cases and errors

Day 3: Frontend

Simple React interface
URL input with validation
Progress indicator
Results table

Day 4: Polish & Export

CSV export functionality
Error handling UI
Summary statistics
Deploy to internal server

Day 5: Testing & Documentation

Test with full NGPF article list
Fix any extraction issues
Create simple user guide

Success Metrics

Extraction Success Rate: >90% of NGPF articles successfully extracted
Processing Speed: <2 seconds per article
Baseline Established: Complete readability scores for all curriculum articles
Export Success: CSV opens correctly in Excel/Google Sheets

Phase 2 (After MVP)
Once baseline is established:

Add comparison mode for original vs. rewritten articles
Track improvement trends over time
Highlight specific problem sentences
Save analysis history for progress tracking