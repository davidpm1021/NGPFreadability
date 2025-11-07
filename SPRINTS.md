# Sprint Plan: NGPF Readability Analyzer

## Sprint 0: Foundation & Setup (1 day)

### Goals
- Establish project structure
- Set up development environments
- Configure testing infrastructure
- Create basic CI/CD pipeline

### Tasks

#### Backend Foundation
- [ ] Create Python project structure
  ```
  /backend
    /app
      __init__.py
      main.py
      /api
        __init__.py
        routes.py
      /core
        __init__.py
        config.py
      /services
        __init__.py
        extraction.py
        readability.py
      /models
        __init__.py
        schemas.py
      /tests
        __init__.py
        test_extraction.py
        test_readability.py
        test_api.py
  requirements.txt
  requirements-dev.txt
  pytest.ini
  .env.example
  ```

- [ ] Create `requirements.txt`:
  ```
  fastapi==0.104.1
  uvicorn[standard]==0.24.0
  trafilatura==1.6.2
  readability-lxml==0.8.1
  textstat==0.7.3
  aiohttp==3.9.1
  pandas==2.1.3
  pydantic==2.5.0
  python-dotenv==1.0.0
  ```

- [ ] Create `requirements-dev.txt`:
  ```
  -r requirements.txt
  pytest==7.4.3
  pytest-asyncio==0.21.1
  pytest-cov==4.1.0
  httpx==0.25.2
  black==23.11.0
  ruff==0.1.6
  mypy==1.7.1
  ```

- [ ] Set up `pytest.ini` with coverage config
- [ ] Create `.env.example` with configuration template
- [ ] Write basic FastAPI health check endpoint

#### Frontend Foundation
- [ ] Initialize Vite + React + TypeScript project
  ```bash
  npm create vite@latest frontend -- --template react-ts
  ```

- [ ] Install dependencies:
  ```bash
  npm install axios papaparse
  npm install -D @types/papaparse tailwindcss postcss autoprefixer
  npm install -D vitest @testing-library/react @testing-library/jest-dom
  npm install -D @testing-library/user-event jsdom
  ```

- [ ] Configure Tailwind CSS
- [ ] Set up Vitest for component testing
- [ ] Create project structure:
  ```
  /frontend
    /src
      /components
        /UrlInput
        /ResultsTable
        /ProgressIndicator
        /ExportButton
      /services
        api.ts
      /types
        index.ts
      /utils
        validation.ts
      /tests
      App.tsx
      main.tsx
    vite.config.ts
    tailwind.config.js
    tsconfig.json
  ```

#### Testing Infrastructure
- [ ] Set up pytest with async support
- [ ] Configure test coverage reporting (target: 80%)
- [ ] Set up Vitest for frontend
- [ ] Create sample test files to verify setup

#### Documentation
- [ ] Create README.md with setup instructions
- [ ] Document environment variables
- [ ] Create CONTRIBUTING.md with development workflow

### Definition of Done
- ✅ Both backend and frontend start successfully
- ✅ Health check endpoint returns 200
- ✅ Sample tests run and pass
- ✅ Linters configured and running
- ✅ Git hooks set up (pre-commit with linting)

---

## Sprint 1: Core Text Extraction (2 days)

### Goals
- Implement reliable text extraction from URLs
- Handle extraction failures gracefully
- Write comprehensive tests for extraction logic

### Tasks

#### Backend: Extraction Service (TDD)
- [ ] **Test**: Write test for successful Trafilatura extraction
- [ ] **Code**: Implement `extract_with_trafilatura(url: str) -> str | None`
- [ ] **Test**: Write test for Trafilatura failure → readability-lxml fallback
- [ ] **Code**: Implement fallback logic
- [ ] **Test**: Write test for complete extraction failure
- [ ] **Code**: Implement error handling and logging
- [ ] **Test**: Write test for timeout handling
- [ ] **Code**: Add timeout configuration (default: 10s)
- [ ] **Test**: Write test for invalid URLs
- [ ] **Code**: Add URL validation

#### Backend: Extraction Models
- [ ] Create Pydantic schemas:
  - `ExtractionRequest` - URL input
  - `ExtractionResult` - extracted text + metadata
  - `ExtractionError` - error details

#### Backend: Async URL Fetching
- [ ] **Test**: Write test for async multi-URL fetching
- [ ] **Code**: Implement `fetch_url_async(session, url)` with aiohttp
- [ ] **Test**: Write test for concurrent request limiting
- [ ] **Code**: Add semaphore to limit concurrent requests (max: 10)
- [ ] **Test**: Write test for retry logic on network errors
- [ ] **Code**: Implement retry with exponential backoff (max 3 attempts)

#### Integration Tests
- [ ] Test extraction with real NGPF article URLs (5-10 samples)
- [ ] Test common failure cases:
  - 404 errors
  - Timeout scenarios
  - Malformed HTML
  - Paywalled content
- [ ] Verify extraction success rate >90% on sample set

#### Documentation
- [ ] Document extraction service API
- [ ] Add examples of successful/failed extractions
- [ ] Document configuration options (timeout, retries, etc.)

### Definition of Done
- ✅ All extraction tests passing (unit + integration)
- ✅ Test coverage >80% for extraction module
- ✅ Successfully extracts text from 90%+ of test URLs
- ✅ Graceful error handling for failures
- ✅ Async fetching works with 100+ URLs

---

## Sprint 2: Readability Analysis Engine (2 days)

### Goals
- Implement all 5 readability metrics
- Validate metric calculations
- Optimize for performance

### Tasks

#### Backend: Readability Service (TDD)
- [ ] **Test**: Write tests for Flesch-Kincaid Grade Level calculation
- [ ] **Code**: Implement `calculate_flesch_kincaid(text: str) -> float`
- [ ] **Test**: Write tests for SMOG Index
- [ ] **Code**: Implement `calculate_smog(text: str) -> float`
- [ ] **Test**: Write tests for Coleman-Liau Index
- [ ] **Code**: Implement `calculate_coleman_liau(text: str) -> float`
- [ ] **Test**: Write tests for ARI
- [ ] **Code**: Implement `calculate_ari(text: str) -> float`
- [ ] **Test**: Write test for consensus calculation
- [ ] **Code**: Implement `calculate_consensus(metrics: dict) -> float`

#### Backend: Text Statistics
- [ ] **Test**: Write tests for word count
- [ ] **Code**: Implement `count_words(text: str) -> int`
- [ ] **Test**: Write tests for sentence count
- [ ] **Code**: Implement `count_sentences(text: str) -> int`
- [ ] **Test**: Write test for syllable counting accuracy
- [ ] **Code**: Verify textstat syllable counting

#### Backend: Complete Analysis Pipeline
- [ ] **Test**: Write test for full analysis of sample text
- [ ] **Code**: Implement `analyze_text(text: str) -> ReadabilityMetrics`
- [ ] Create `ReadabilityMetrics` Pydantic model:
  ```python
  class ReadabilityMetrics(BaseModel):
      flesch_kincaid_grade: float
      smog: float
      coleman_liau: float
      ari: float
      consensus: float
      word_count: int
      sentence_count: int
  ```

#### Validation & Testing
- [ ] Test with known-grade-level texts (elementary, high school, college)
- [ ] Verify metric calculations match expected ranges
- [ ] Test edge cases:
  - Very short text (<100 words)
  - Very long text (>10,000 words)
  - Text with no punctuation
  - Text with unusual formatting

#### Performance Optimization
- [ ] **Test**: Write performance test (target: <100ms per article)
- [ ] **Code**: Profile and optimize if needed
- [ ] Add caching for repeated text analysis (optional)

### Definition of Done
- ✅ All 5 readability metrics calculated correctly
- ✅ Test coverage >80% for readability module
- ✅ Metrics validated against known-grade texts
- ✅ Performance meets <100ms per article target
- ✅ Edge cases handled gracefully

---

## Sprint 3: API Endpoint Integration (1.5 days)

### Goals
- Create `/api/analyze-urls` endpoint
- Integrate extraction + readability services
- Implement async batch processing

### Tasks

#### Backend: Data Models
- [ ] Create `UrlAnalysisRequest` schema:
  ```python
  class UrlAnalysisRequest(BaseModel):
      urls: list[str]

      @validator('urls')
      def validate_urls(cls, v):
          # URL validation logic
  ```

- [ ] Create `ArticleAnalysis` schema:
  ```python
  class ArticleAnalysis(BaseModel):
      url: str
      title: str | None
      extraction_success: bool
      metrics: ReadabilityMetrics | None
      error: str | None
  ```

- [ ] Create `AnalysisSummary` schema:
  ```python
  class AnalysisSummary(BaseModel):
      total_urls: int
      successful: int
      failed: int
      average_grade_level: float | None
  ```

- [ ] Create `BatchAnalysisResponse` schema

#### Backend: API Endpoint (TDD)
- [ ] **Test**: Write test for single URL analysis
- [ ] **Code**: Implement basic endpoint structure
- [ ] **Test**: Write test for batch URL analysis (10 URLs)
- [ ] **Code**: Implement async batch processing with `asyncio.gather()`
- [ ] **Test**: Write test for progress tracking
- [ ] **Code**: Add progress callback mechanism (optional for MVP)
- [ ] **Test**: Write test for partial failures (some URLs succeed, some fail)
- [ ] **Code**: Handle partial failures, return all results
- [ ] **Test**: Write test for request validation (invalid URLs)
- [ ] **Code**: Add input validation and error responses

#### Backend: Core Processing Function
- [ ] **Test**: Write test for `process_url(session, url)` end-to-end
- [ ] **Code**: Implement complete pipeline:
  1. Fetch URL
  2. Extract text
  3. Calculate metrics
  4. Return ArticleAnalysis
- [ ] Add error handling at each stage
- [ ] Add logging for debugging

#### Integration Tests
- [ ] Test endpoint with 100+ URLs to verify performance
- [ ] Test concurrent request handling
- [ ] Test memory usage with large batches
- [ ] Verify response format matches specification

#### CORS & Configuration
- [ ] Configure CORS for frontend access
- [ ] Add rate limiting (optional for internal tool)
- [ ] Add request size limits

### Definition of Done
- ✅ `/api/analyze-urls` endpoint working end-to-end
- ✅ Successfully processes 100+ URLs in <3 minutes
- ✅ Test coverage >80% for API module
- ✅ Proper error handling for all failure scenarios
- ✅ API documentation (OpenAPI/Swagger) auto-generated

---

## Sprint 4: Frontend UI Components (2 days)

### Goals
- Build URL input interface
- Create results table display
- Implement progress indicators

### Tasks

#### Type Definitions
- [ ] Create TypeScript interfaces matching backend schemas:
  ```typescript
  interface ReadabilityMetrics {
    flesch_kincaid_grade: number;
    smog: number;
    coleman_liau: number;
    ari: number;
    consensus: number;
    word_count: number;
    sentence_count: number;
  }

  interface ArticleAnalysis {
    url: string;
    title: string | null;
    extraction_success: boolean;
    metrics: ReadabilityMetrics | null;
    error: string | null;
  }

  interface AnalysisSummary {
    total_urls: number;
    successful: number;
    failed: number;
    average_grade_level: number | null;
  }
  ```

#### Component 1: URL Input (TDD)
- [ ] **Test**: Render empty textarea
- [ ] **Code**: Create `UrlInput` component
- [ ] **Test**: Parse URLs from textarea (one per line)
- [ ] **Code**: Implement URL parsing logic
- [ ] **Test**: Validate URL format
- [ ] **Code**: Add URL validation with feedback
- [ ] **Test**: Display count of valid URLs
- [ ] **Code**: Show "X valid URLs detected" message
- [ ] **Test**: Clear functionality
- [ ] **Code**: Add clear button
- [ ] Style with Tailwind CSS

#### Component 2: Progress Indicator (TDD)
- [ ] **Test**: Display processing status
- [ ] **Code**: Create `ProgressIndicator` component
- [ ] **Test**: Show "Processing X of Y articles..."
- [ ] **Code**: Implement progress counter
- [ ] **Test**: Show completion message
- [ ] **Code**: Add success/completion state
- [ ] Style with loading spinner

#### Component 3: Results Table (TDD)
- [ ] **Test**: Render empty state
- [ ] **Code**: Create `ResultsTable` component
- [ ] **Test**: Display results in table format
- [ ] **Code**: Implement table with columns:
  - URL (truncated)
  - Title
  - FK Grade | SMOG | Coleman-Liau | ARI | Consensus
  - Word Count
  - Status (✓/✗)
- [ ] **Test**: Handle empty results
- [ ] **Test**: Handle failed extractions (display error)
- [ ] **Code**: Add error row styling
- [ ] **Test**: Sort by column
- [ ] **Code**: Implement column sorting
- [ ] Style with Tailwind CSS (responsive)

#### Component 4: Summary Stats (TDD)
- [ ] **Test**: Display summary statistics
- [ ] **Code**: Create `SummaryStats` component
- [ ] **Test**: Show average grade level
- [ ] **Code**: Display with grade level interpretation (e.g., "10.8 - High School")
- [ ] **Test**: Show success/failure counts
- [ ] **Code**: Display total, successful, failed counts
- [ ] Style with highlight box

#### Component 5: Analyze Button
- [ ] **Test**: Button disabled when no URLs
- [ ] **Code**: Create `AnalyzeButton` with validation
- [ ] **Test**: Button shows loading state
- [ ] **Code**: Add loading spinner during processing
- [ ] **Test**: Button disabled during processing
- [ ] Style with primary action appearance

#### Integration
- [ ] Combine all components in `App.tsx`
- [ ] Implement state management (useState or context)
- [ ] Add responsive layout
- [ ] Test full user flow

### Definition of Done
- ✅ All components render correctly
- ✅ Component test coverage >80%
- ✅ Responsive design works on mobile/tablet/desktop
- ✅ UI matches design mockup from PRD
- ✅ Accessibility basics (keyboard navigation, ARIA labels)

---

## Sprint 5: API Integration & CSV Export (1.5 days)

### Goals
- Connect frontend to backend API
- Implement CSV export functionality
- Handle loading and error states

### Tasks

#### API Service Layer (TDD)
- [ ] **Test**: Mock API call to `/api/analyze-urls`
- [ ] **Code**: Create `api.ts` service:
  ```typescript
  export const analyzeUrls = async (
    urls: string[]
  ): Promise<BatchAnalysisResponse> => {
    // axios implementation
  }
  ```
- [ ] **Test**: Handle successful response
- [ ] **Code**: Parse and return typed response
- [ ] **Test**: Handle API errors (network, 500, etc.)
- [ ] **Code**: Add error handling with user-friendly messages
- [ ] **Test**: Handle timeout
- [ ] **Code**: Add timeout configuration (60s)

#### Frontend-Backend Integration
- [ ] Connect `AnalyzeButton` onClick to API call
- [ ] Update `ProgressIndicator` during API call
- [ ] Display results in `ResultsTable` on success
- [ ] Show error message on failure
- [ ] Test with real backend (end-to-end)

#### CSV Export (TDD)
- [ ] **Test**: Generate CSV from results
- [ ] **Code**: Create `exportToCSV(results: ArticleAnalysis[])` utility
- [ ] **Test**: CSV includes all columns
- [ ] **Code**: Use PapaParse to generate CSV with headers:
  - URL, Title, FK Grade, SMOG, Coleman-Liau, ARI, Consensus, Word Count, Sentence Count, Status
- [ ] **Test**: Handle special characters in CSV
- [ ] **Code**: Proper CSV escaping
- [ ] **Test**: Trigger browser download
- [ ] **Code**: Create `ExportButton` component with download logic
- [ ] **Test**: Disabled when no results
- [ ] Add filename with timestamp: `ngpf-readability-analysis-2024-11-07.csv`

#### Error Handling & User Feedback
- [ ] Display loading spinner during analysis
- [ ] Show error toast for API failures
- [ ] Display inline errors for failed URL extractions
- [ ] Add "Retry" button for failed requests
- [ ] Clear previous results on new analysis

#### Polish
- [ ] Add animations for loading states
- [ ] Improve empty states
- [ ] Add helpful error messages
- [ ] Test with various data sizes (1, 10, 100 URLs)

### Definition of Done
- ✅ Frontend successfully calls backend API
- ✅ Results display correctly from real data
- ✅ CSV export works and opens in Excel/Sheets
- ✅ Error handling covers all failure scenarios
- ✅ Test coverage >80% for integration code
- ✅ End-to-end test with 50+ URLs successful

---

## Sprint 6: Testing, Polish & Deployment (1 day)

### Goals
- Comprehensive testing with real NGPF URLs
- Bug fixes and edge case handling
- Deployment preparation

### Tasks

#### Backend Testing
- [ ] Create test dataset with 20+ real NGPF article URLs
- [ ] Run full analysis and verify results
- [ ] Test edge cases:
  - URLs requiring redirects
  - HTTPS vs HTTP
  - URLs with query parameters
  - Articles behind soft paywalls
- [ ] Fix any extraction failures
- [ ] Verify extraction success rate >90%
- [ ] Performance test with 100+ URLs
- [ ] Verify response time <2s per article average

#### Frontend Testing
- [ ] Manual testing of full user workflow
- [ ] Test with different browsers (Chrome, Firefox, Safari)
- [ ] Test responsive design on mobile
- [ ] Test CSV export in Excel and Google Sheets
- [ ] Fix any UI bugs or layout issues
- [ ] Accessibility audit (screen reader, keyboard nav)

#### Integration Testing
- [ ] End-to-end test: paste URLs → analyze → export CSV
- [ ] Test with large batch (100+ URLs)
- [ ] Verify memory usage is acceptable
- [ ] Test concurrent users (if relevant)

#### Documentation
- [ ] Update README with:
  - Setup instructions
  - Usage guide
  - Troubleshooting common issues
- [ ] Add API documentation examples
- [ ] Create user guide with screenshots
- [ ] Document known limitations

#### Deployment Preparation
- [ ] Create production environment config
- [ ] Set up environment variables for production
- [ ] Configure production CORS settings
- [ ] Add health check endpoint monitoring
- [ ] Create deployment script/Docker setup (if needed)
- [ ] Test deployment on staging environment

#### Final Polish
- [ ] Fix any remaining bugs from testing
- [ ] Improve error messages based on testing feedback
- [ ] Add any missing loading indicators
- [ ] Final UI polish (spacing, colors, fonts)
- [ ] Code cleanup and remove console.logs

### Definition of Done
- ✅ All tests passing (backend + frontend)
- ✅ Extraction success rate >90% on NGPF articles
- ✅ CSV export verified in Excel/Google Sheets
- ✅ Documentation complete and accurate
- ✅ Application deployed to staging/production
- ✅ User acceptance testing passed
- ✅ Performance meets requirements (<2s per article)

---

## Sprint 7: MVP Release & Handoff (0.5 days)

### Goals
- Deploy to production
- Create baseline analysis of NGPF curriculum
- Handoff to users

### Tasks

#### Production Deployment
- [ ] Deploy backend to production server
- [ ] Deploy frontend to production
- [ ] Verify production environment works
- [ ] Test with production URLs
- [ ] Monitor for errors

#### Baseline Analysis
- [ ] Obtain complete list of NGPF curriculum articles
- [ ] Run full analysis on all articles
- [ ] Export results to CSV
- [ ] Share baseline data with stakeholders
- [ ] Document any problematic URLs for manual review

#### User Handoff
- [ ] Create user documentation
- [ ] Train users on tool usage
- [ ] Share access credentials/URLs
- [ ] Set up feedback mechanism
- [ ] Schedule follow-up review

#### Post-Launch
- [ ] Monitor usage and errors
- [ ] Collect user feedback
- [ ] Document bugs/feature requests for Phase 2
- [ ] Celebrate MVP completion! 🎉

### Definition of Done
- ✅ Tool deployed and accessible to users
- ✅ Baseline readability analysis complete
- ✅ Users trained and documentation provided
- ✅ Monitoring in place for production issues
- ✅ Phase 2 backlog created

---

## Summary Timeline

| Sprint | Duration | Focus Area |
|--------|----------|------------|
| Sprint 0 | 1 day | Foundation & Setup |
| Sprint 1 | 2 days | Text Extraction |
| Sprint 2 | 2 days | Readability Analysis |
| Sprint 3 | 1.5 days | API Integration |
| Sprint 4 | 2 days | Frontend UI |
| Sprint 5 | 1.5 days | Export & Polish |
| Sprint 6 | 1 day | Testing & Deployment |
| Sprint 7 | 0.5 days | Release & Handoff |
| **Total** | **11.5 days** | **MVP Complete** |

## Success Criteria

### Technical Metrics
- ✅ Test coverage >80% across all modules
- ✅ Extraction success rate >90%
- ✅ Processing speed <2s per article
- ✅ Handle 100+ URLs in single batch
- ✅ CSV export works in Excel/Sheets

### User Metrics
- ✅ Complete baseline analysis of NGPF curriculum
- ✅ Tool adopted by content team
- ✅ Positive user feedback
- ✅ Identified improvement opportunities for Phase 2

## Phase 2 Roadmap (Future)
- Comparison mode (original vs. rewritten)
- Trend tracking over time
- Sentence-level highlighting
- Analysis history persistence
- Advanced reporting/dashboards
