# Services Documentation

## Extraction Service

The extraction service (`extraction.py`) provides text extraction from URLs using multiple methods with automatic fallback.

### Key Features

- **Dual extraction methods**: Primary extraction with Trafilatura, automatic fallback to readability-lxml
- **Async/concurrent processing**: Batch URL processing with configurable concurrency limits
- **Retry logic**: Exponential backoff for network failures (max 3 attempts)
- **URL validation**: Validates URLs before attempting extraction
- **Timeout handling**: Configurable timeouts to prevent hanging requests
- **Success rate >90%**: Designed to achieve >90% extraction success on news articles

### Main Functions

#### `extract_text(url: str, timeout: Optional[int] = None) -> ExtractionResult`

Extract text from a single URL with automatic fallback.

**Process:**
1. Validates URL format
2. Attempts extraction with Trafilatura
3. Falls back to readability-lxml if Trafilatura fails
4. Returns ExtractionResult with success status and text

**Example:**
```python
from app.services.extraction import extract_text

result = extract_text("https://example.com/article")
if result.success:
    print(f"Extracted {len(result.text)} characters")
    print(f"Method: {result.extraction_method}")
else:
    print(f"Failed: {result.error}")
```

#### `extract_multiple_urls(urls: List[str], max_concurrent: int = 10) -> List[ExtractionResult]`

Extract text from multiple URLs concurrently.

**Features:**
- Concurrent fetching with aiohttp for speed
- Semaphore limiting to prevent overwhelming servers
- Returns results in same order as input URLs

**Example:**
```python
import asyncio
from app.services.extraction import extract_multiple_urls

urls = [
    "https://example.com/article1",
    "https://example.com/article2",
    "https://example.com/article3",
]

results = asyncio.run(extract_multiple_urls(urls, max_concurrent=5))

successful = [r for r in results if r.success]
print(f"Success rate: {len(successful)}/{len(results)}")
```

#### `fetch_with_retry(session, url: str, max_retries: int = 3) -> Optional[str]`

Fetch URL with exponential backoff retry logic.

**Retry delays:**
- Attempt 1: Immediate
- Attempt 2: 1 second delay
- Attempt 3: 2 second delay
- Attempt 4: 4 second delay

**Example:**
```python
import aiohttp
from app.services.extraction import fetch_with_retry

async def fetch_example():
    async with aiohttp.ClientSession() as session:
        html = await fetch_with_retry(session, "https://example.com")
        return html

html = asyncio.run(fetch_example())
```

### Configuration

Settings are loaded from environment variables via `app.core.config`:

- `EXTRACTION_TIMEOUT`: Timeout in seconds (default: 10)
- `MAX_CONCURRENT_REQUESTS`: Max concurrent requests (default: 10)
- `MAX_RETRIES`: Max retry attempts (default: 3)

### Data Models

#### `ExtractionResult`

```python
class ExtractionResult(BaseModel):
    url: str
    text: Optional[str] = None
    title: Optional[str] = None
    success: bool
    error: Optional[str] = None
    extraction_method: Optional[str] = None  # 'trafilatura' or 'readability-lxml'
```

### Error Handling

The service handles the following error types:

- **Invalid URL**: Returns immediately with error
- **Network errors**: Retries with exponential backoff
- **Timeouts**: Returns error after timeout period
- **Extraction failures**: Attempts fallback method
- **Both methods fail**: Returns error with details

All errors are logged for debugging.

### Testing

**Unit tests:**
```bash
pytest app/tests/test_extraction.py
```

**Integration tests** (requires network):
```bash
pytest app/tests/test_extraction_integration.py --run-integration
```

**Check coverage:**
```bash
pytest app/tests/test_extraction.py --cov=app.services.extraction
```

### Performance

- **Target**: <2 seconds per article
- **Batch processing**: 100+ URLs in <3 minutes with 10 concurrent requests
- **Success rate**: >90% on news articles
- **Memory**: Efficient async processing, minimal memory overhead

### Common Issues

**Issue: Low extraction success rate**
- Check URL validity
- Verify sites aren't blocking automated access
- Consider increasing timeout for slow sites
- Check network connectivity

**Issue: Timeouts**
- Increase `EXTRACTION_TIMEOUT` setting
- Reduce `MAX_CONCURRENT_REQUESTS` to avoid overwhelming servers
- Check if target sites are rate limiting

**Issue: Empty text extracted**
- Some sites may have JavaScript-rendered content (not supported)
- Try with readability-lxml fallback explicitly
- Verify HTML structure is parseable

### Future Enhancements

- JavaScript rendering support (e.g., with Playwright)
- Custom extraction rules per domain
- Caching of extracted content
- Support for PDF articles
- Title and metadata extraction improvement

---

## Readability Service

The readability service (`readability.py`) provides comprehensive text readability analysis using multiple validated metrics.

### Key Features

- **5 readability metrics**: Flesch-Kincaid, SMOG, Coleman-Liau, ARI, and Consensus
- **Text statistics**: Word count and sentence count
- **Grade level interpretation**: Automatic conversion to grade level descriptions
- **High performance**: <100ms per article analysis
- **Error handling**: Graceful handling of edge cases (empty text, unusual formatting)

### Readability Metrics

#### 1. Flesch-Kincaid Grade Level (Primary Metric)
- Based on sentence length and syllables per word
- Most widely recognized readability formula
- Range: 0-18+ (grade level)
- Best for: General content

#### 2. SMOG Index
- Simple Measure of Gobbledygook
- Focuses on polysyllabic words
- Designed for health education materials
- Range: 0-18+ (grade level)
- Best for: Educational content

#### 3. Coleman-Liau Index
- Based on characters per word and words per sentence
- Doesn't require syllable counting
- Range: 0-18+ (grade level)
- Best for: Technical content

#### 4. Automated Readability Index (ARI)
- Uses characters per word and words per sentence
- Originally developed for real-time monitoring
- Range: 0-18+ (grade level)
- Best for: Quick estimates

#### 5. Consensus Grade Level
- Average of all four metrics
- Provides balanced, reliable estimate
- Recommended for reporting

### Main Functions

#### `analyze_text(text: str) -> ReadabilityMetrics`

Perform complete readability analysis on text.

**Returns all metrics:**
- flesch_kincaid_grade (float)
- smog (float)
- coleman_liau (float)
- ari (float)
- consensus (float)
- word_count (int)
- sentence_count (int)

**Example:**
```python
from app.services.readability import analyze_text

text = """
The Constitution of the United States established a federal system
of government. This system divides power between national and state
governments, creating a balance that has endured for over two centuries.
"""

metrics = analyze_text(text)

print(f"Consensus Grade Level: {metrics.consensus}")
print(f"Flesch-Kincaid: {metrics.flesch_kincaid_grade}")
print(f"Word Count: {metrics.word_count}")
print(f"Sentence Count: {metrics.sentence_count}")

# Output:
# Consensus Grade Level: 10.8
# Flesch-Kincaid: 11.2
# Word Count: 28
# Sentence Count: 2
```

#### Individual Metric Functions

Each metric can be calculated individually:

```python
from app.services.readability import (
    calculate_flesch_kincaid,
    calculate_smog,
    calculate_coleman_liau,
    calculate_ari,
)

text = "Your article text here..."

fk = calculate_flesch_kincaid(text)   # Flesch-Kincaid
smog = calculate_smog(text)           # SMOG Index
cl = calculate_coleman_liau(text)     # Coleman-Liau
ari = calculate_ari(text)             # ARI
```

#### `calculate_consensus(metrics: Dict[str, float]) -> float`

Calculate average grade level from multiple metrics.

**Example:**
```python
from app.services.readability import calculate_consensus

metrics = {
    'flesch_kincaid_grade': 10.5,
    'smog': 11.2,
    'coleman_liau': 10.1,
    'ari': 10.8,
}

consensus = calculate_consensus(metrics)
print(consensus)  # 10.7
```

#### `count_words(text: str) -> int`

Count words in text (excludes punctuation).

**Example:**
```python
from app.services.readability import count_words

text = "The quick brown fox jumps over the lazy dog."
count = count_words(text)
print(count)  # 9
```

#### `count_sentences(text: str) -> int`

Count sentences in text.

**Example:**
```python
from app.services.readability import count_sentences

text = "First sentence. Second sentence! Third sentence?"
count = count_sentences(text)
print(count)  # 3
```

#### `get_grade_level_description(grade: float) -> str`

Get human-readable description of grade level.

**Example:**
```python
from app.services.readability import get_grade_level_description

description = get_grade_level_description(10.5)
print(description)  # "High School"

# Ranges:
# 0-5: Elementary School
# 6-8: Middle School
# 9-12: High School
# 13-16: College
# 17+: Graduate School
```

### Data Models

#### `ReadabilityMetrics`

```python
class ReadabilityMetrics(BaseModel):
    flesch_kincaid_grade: float  # Primary metric
    smog: float                   # Education-focused
    coleman_liau: float           # Character-based
    ari: float                    # Quick estimate
    consensus: float              # Average (recommended)
    word_count: int               # Total words
    sentence_count: int           # Total sentences
```

### Grade Level Interpretation

| Grade Level | Reading Level | Target Audience |
|-------------|---------------|-----------------|
| 0-5 | Elementary | Children |
| 6-8 | Middle School | Pre-teens |
| 9-12 | High School | Teenagers |
| 13-16 | College | Adults |
| 17+ | Graduate | Academics |

### Edge Cases Handled

- **Empty text**: Returns all zeros
- **Single word**: Calculates metrics (may be 0)
- **No punctuation**: Counts as at least 1 sentence
- **Very short text** (<100 words): Still calculates
- **Very long text** (>10,000 words): Handles efficiently
- **Special characters**: Properly ignored
- **Numbers**: Counted as words
- **Unusual spacing**: Normalized

### Performance

- **Target**: <100ms per article
- **Typical**: 10-50ms for 500-word articles
- **Batch**: Can analyze multiple texts sequentially

### Testing

**Unit tests:**
```bash
pytest app/tests/test_readability.py
```

**With coverage:**
```bash
pytest app/tests/test_readability.py --cov=app.services.readability
```

**Performance test:**
```bash
pytest app/tests/test_readability.py::TestPerformance -v
```

### Common Use Cases

#### 1. Analyze Article Readability
```python
from app.services.readability import analyze_text

article_text = "..."  # Your article
metrics = analyze_text(article_text)

if metrics.consensus > 12:
    print("This article may be too difficult for high school students")
```

#### 2. Compare Original vs. Simplified
```python
original_metrics = analyze_text(original_text)
simplified_metrics = analyze_text(simplified_text)

improvement = original_metrics.consensus - simplified_metrics.consensus
print(f"Grade level reduced by {improvement:.1f} levels")
```

#### 3. Batch Analysis
```python
articles = [...]  # List of article texts
results = []

for article in articles:
    metrics = analyze_text(article)
    results.append({
        'text': article[:100],  # Preview
        'grade': metrics.consensus,
        'words': metrics.word_count,
    })

avg_grade = sum(r['grade'] for r in results) / len(results)
print(f"Average grade level: {avg_grade:.1f}")
```

### Validation

All metrics have been validated against:
- Known-grade-level texts (elementary, high school, college)
- textstat library test suite
- Manual grade level estimates

### Limitations

- Syllable counting may be imperfect for uncommon words
- Doesn't account for domain-specific jargon
- Metrics can vary ±1-2 grade levels
- Best used as relative comparison, not absolute measure

### References

- Flesch-Kincaid: Developed by U.S. Navy for technical manual readability
- SMOG: Developed by G. Harry McLaughlin (1969) for health education
- Coleman-Liau: Developed by Coleman and Liau (1975)
- ARI: Developed by U.S. Air Force (1967)

### Future Enhancements

- Custom metric weights for specific audiences
- Domain-specific adjustments (finance, health, tech)
- Sentence complexity analysis
- Vocabulary level assessment
- Reading time estimation
