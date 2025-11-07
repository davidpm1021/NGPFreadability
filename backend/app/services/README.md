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
