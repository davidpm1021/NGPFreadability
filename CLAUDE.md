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
- Tailwind CSS - Styling (with dark mode)
- PapaParse - CSV handling
- localStorage - Client-side caching and theme persistence

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
1. **Frontend** → User pastes URLs (one per line), validates format
2. **URL Filtering** → Silently removes YouTube, EdPuzzle, Instagram, images, infographics
3. **Cache Check** → Checks localStorage for previously analyzed URLs (7-day expiry)
4. **Backend API** (`POST /api/analyze-urls`) → Sends only uncached URLs
5. **Backend Filtering** → Double-checks and filters non-article URLs
6. **Async Processing** → Parallel fetching with aiohttp for speed (<2s per article)
7. **Text Extraction** → Trafilatura primary, readability-lxml fallback
8. **Readability Analysis** → textstat calculates 5 metrics per article
9. **Response** → JSON with metrics, statistics, summary, and failed URLs
10. **Cache Update** → Stores new results in localStorage
11. **Result Merging** → Combines cached + new results
12. **Frontend Display** → Table view + CSV export with dark mode support

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

### URL Filtering (Silent)
**URLs that are automatically skipped (not shown in results):**
- YouTube videos (all formats: youtube.com, youtu.be)
- EdPuzzle videos (edpuzzle.com)
- Instagram posts (instagram.com)
- Direct image files (.png, .jpg, .jpeg, .gif, .webp, .svg, .bmp)
- Infographic platforms (infogram.com, datawrapper.de, tableau.com)
- Trailing punctuation is automatically removed from URLs ()[].,;

**URLs that show as "Failed" in results with specific error messages:**
- **Homepages:** "Homepage URLs cannot be analyzed - please use article URLs"
- **Access denied (403):** "Access denied - site may be blocking scrapers"
- **Paywall (402):** "Paywall detected - subscription required"
- **Not found (404):** "Page not found (404)"
- **Rate limited (429):** "Rate limited - too many requests"
- **Server errors (5xx):** "Server error (status code)"
- **Timeout:** "Request timed out - server too slow"
- **SSL issues:** "SSL/TLS error - certificate issue"
- **Connection issues:** "Connection failed - check URL or network"
- **No content:** "No text content found - page may require JavaScript"
- **Generic:** "Extraction error: ErrorType"

### Text Extraction
- **Trafilatura** is primary (confirmed 95.8% accuracy)
- Use `extract(downloaded, include_comments=False, include_tables=False, no_fallback=False)`
- **No JavaScript rendering needed** - confirmed by user
- Fallback to readability-lxml only if Trafilatura fails
- URL cleaning removes trailing punctuation before extraction

### Client-Side Caching
- **Storage:** localStorage with key `ngpf-readability-cache`
- **Expiry:** 7 days from analysis
- **Version:** 1.0 (clears on version mismatch)
- **Resume capability:** Re-paste URLs to continue after timeout
- **Cache operations:** getCachedResults(), cacheResults(), clearCache(), getCacheStats()
- **Merge logic:** Combines cached + new results, recalculates summary statistics

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

**Sprint 6 Complete + Enhancements** ✅ - Dark mode, client-side caching, and smart URL filtering added.

**Latest Update (Post-Sprint 6):**
- Dark mode with theme toggle and localStorage persistence
- Client-side caching for timeout recovery (7-day expiry, resume capability)
- Smart URL filtering (silently skips YouTube, EdPuzzle, Instagram, images, infographics)
- Fixed summary statistics bugs (NaN success rate, static grade level)
- Improved URL validation (less aggressive, allows more legitimate articles)
- Dynamic timeout calculation (15s per URL + buffer, max 30 min)
- Clear cache button in UI
- All components have dark mode variants

**Sprint 0 - Foundation (✅ Complete):**
- Backend project structure with FastAPI, pytest, and all dependencies configured
- Frontend React/TypeScript project with Vite, Tailwind CSS, and Vitest
- Basic health check endpoint (`/health`) working
- Type definitions for API contracts
- Utility functions with tests (validation.ts)
- Development environment configured for both backend and frontend

**Sprint 1 - Text Extraction (✅ Complete):**
- Extraction service (`app/services/extraction.py`) with dual-method approach
- Trafilatura as primary extraction method
- readability-lxml as automatic fallback
- Async URL fetching with aiohttp for concurrent processing
- Semaphore-based concurrency limiting (configurable, default: 10)
- Retry logic with exponential backoff (max 3 attempts)
- URL validation before extraction
- Timeout handling (configurable, default: 10s)
- Comprehensive unit tests (70+ test cases covering all scenarios)
- Integration tests with real URLs and success rate validation
- Complete service documentation with examples

**Testing Coverage:**
- Unit tests: `test_extraction.py` (mocked, fast)
- Integration tests: `test_extraction_integration.py` (requires `--run-integration` flag)
- All edge cases covered: timeouts, failures, invalid URLs, retries
- Success rate calculation for validation

**Known Issues:**
- Python 3.11+ needs to be installed on system before tests can run
- Backend server cannot start until Python is installed
- Integration tests cannot be executed until Python is available

**Sprint 2 - Readability Analysis (✅ Complete):**
- Readability service (`app/services/readability.py`) with 5 metrics
- Flesch-Kincaid Grade Level (primary metric)
- SMOG Index (education-focused)
- Coleman-Liau Index (character-based)
- Automated Readability Index (ARI)
- Consensus grade level (average of all 4 metrics)
- Word count and sentence count statistics
- Grade level descriptions (Elementary, Middle School, etc.)
- Comprehensive unit tests (100+ test cases)
- Performance validation (<100ms per article)
- Known-grade-level text validation (elementary, high school, college)
- Edge case handling (empty, short, long, no punctuation)
- Complete documentation with examples and use cases

**Sprint 3 - API Endpoint Integration (✅ Complete):**
- `/api/analyze-urls` endpoint fully implemented
- Complete pipeline: URL → extract → analyze → response
- process_url() function integrating extraction + readability
- Request/response Pydantic schemas with validation
- UrlAnalysisRequest (1-200 URLs)
- ArticleAnalysis (complete result per URL)
- AnalysisSummary (total, successful, failed, avg grade)
- BatchAnalysisResponse (results + summary)
- Comprehensive API tests (40+ test cases)
- Single URL, batch, partial failures, validation errors
- Summary calculation tests
- Sequential processing (handles 100+ URLs)
- Auto-generated OpenAPI/Swagger documentation
- Complete API documentation with examples
- Python, JavaScript, curl examples
- Error handling and troubleshooting guide

**Sprint 4 - Frontend UI Components (✅ Complete):**
- All React components built with Tailwind CSS
- UrlInput: Textarea with URL validation, count display, clear button
- ProgressIndicator: Loading spinner with progress bar and percentage
- ResultsTable: Full results table with all metrics, truncated URLs, status icons
- SummaryStats: Grade level cards with totals, success/fail counts
- ExportButton: CSV export with PapaParse, timestamped filenames
- Main App component with complete state management
- API integration with analyzeUrls service
- Error handling and user feedback
- Responsive design (mobile/tablet/desktop)
- Full user flow working end-to-end

**Next Steps (Sprint 5):**
1. Install Python 3.11+ to run backend and test full stack
2. Polish UI and add loading states
3. Implement error handling improvements
4. Add CSV export validation
5. End-to-end testing with real backend



# Testing Strategy
- Write tests BEFORE implementation (TDD)
- Unit tests for all utilities
- Integration tests for API endpoints
- Component tests with React Testing Library
- Minimum 80% coverage requirement