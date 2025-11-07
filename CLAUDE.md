# CLAUDE.md

Update this document with the current status after every commit.

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**NGPF Article Readability Analyzer** - Internal tool to analyze readability metrics for articles linked in NGPF curriculum. Processes bulk URLs to extract text and calculate multiple readability scores (Flesch-Kincaid, SMOG, Coleman-Liau, ARI) for baseline comparison with future simplified versions.

## Tech Stack

**Backend (Python):**
- FastAPI - API framework
- Trafilatura - Primary text extraction (95.8% accuracy)
- readability-lxml - Fallback extractor
- textstat - Readability calculations
- aiohttp - Async URL fetching
- pandas - CSV generation

**Frontend (React):**
- React + TypeScript
- Axios - API calls
- Tailwind CSS - Styling
- PapaParse - CSV handling

## Development Commands

### Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn trafilatura readability-lxml textstat aiohttp pandas

# Run development server
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Testing
```bash
# Test with sample URLs (backend)
python test_extraction.py

# Run frontend tests
cd frontend
npm test
```

## Architecture

### Request Flow
1. **Frontend** → User pastes URLs (one per line), validates format, sends to backend
2. **Backend API** (`POST /api/analyze-urls`) → Receives URL list
3. **Async Processing** → Parallel fetching with aiohttp for speed (<2s per article)
4. **Text Extraction** → Trafilatura primary, readability-lxml fallback
5. **Readability Analysis** → textstat calculates 5 metrics per article
6. **Response** → JSON with metrics, statistics, summary, and failed URLs
7. **Frontend Display** → Table view + CSV export

### Key Backend Components

**`process_url(session, url)`** - Core async function:
- Fetches URL content
- Extracts clean text (removes ads/navigation)
- Calculates: flesch_kincaid_grade, smog, coleman_liau, ari, consensus
- Returns statistics: word_count, sentence_count
- Handles failures gracefully (returns extraction_success: false)

**`/api/analyze-urls` endpoint:**
- Accepts list of URLs
- Processes all concurrently with asyncio.gather()
- Returns results array + summary (total, successful, failed, average_grade_level)

### Data Structures

**Request:**
```json
{
  "urls": ["https://example.com/article1", ...]
}
```

**Response:**
```json
{
  "results": [{
    "url": "...",
    "title": "...",
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
  }],
  "summary": {
    "total_urls": 87,
    "successful": 84,
    "failed": 3,
    "average_grade_level": 10.8
  }
}
```

## Important Implementation Details

### Text Extraction
- **Trafilatura** is primary (confirmed 95.8% accuracy)
- Use `extract(downloaded, include_comments=False, include_tables=False, no_fallback=False)`
- **No JavaScript rendering needed** - confirmed by user
- Fallback to readability-lxml only if Trafilatura fails

### Readability Metrics Priority
1. **Flesch-Kincaid Grade Level** - Primary metric
2. SMOG Index - Education-focused
3. Coleman-Liau Index
4. Automated Readability Index (ARI)
5. Consensus - Average of all four

### Performance Requirements
- **Extraction success rate:** >90% of NGPF articles
- **Processing speed:** <2 seconds per article
- **Batch support:** Handle 100+ URLs in single request
- Use async/await throughout for parallel processing

### UI Requirements
- Large textarea for bulk URL input (one per line)
- Real-time progress: "Processing 23 of 87 articles..."
- Results table with columns: URL | Title | FK | SMOG | CL | ARI | Consensus | Word Count | Status
- CSV export with all data
- Summary statistics showing average grade level
- Failed URLs listed separately for manual review

## Development Workflow

### MVP Implementation Order (5 days)
1. **Day 1-2:** Backend core - FastAPI + Trafilatura + textstat pipeline
2. **Day 3:** Frontend - React interface with URL input and results table
3. **Day 4:** CSV export + error handling UI + summary stats
4. **Day 5:** Testing with full NGPF article list + bug fixes

### Testing Strategy
- Start with 10-20 NGPF article URLs during development
- Test edge cases: paywalls, 404s, malformed URLs
- Verify CSV opens correctly in Excel/Google Sheets
- Final test with complete NGPF curriculum article list

## Phase 2 Features (Post-MVP)
After baseline is established:
- Comparison mode for original vs. rewritten articles
- Trend tracking over time
- Sentence-level problem highlighting
- Analysis history persistence

## Current Status

**Project initialized** - Repository created with PRD. No code yet.

**Next Steps:**
1. Set up backend project structure with FastAPI
2. Implement core text extraction with Trafilatura
3. Add readability calculations with textstat
4. Create `/api/analyze-urls` endpoint
5. Set up React frontend project



# Testing Strategy
- Write tests BEFORE implementation (TDD)
- Unit tests for all utilities
- Integration tests for API endpoints
- Component tests with React Testing Library
- Minimum 80% coverage requirement