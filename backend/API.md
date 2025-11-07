# API Documentation

## NGPF Readability Analyzer API

Base URL: `http://localhost:8000`

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Endpoints

### Health Check

#### `GET /health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy"
}
```

**Status Codes:**
- `200 OK` - API is healthy

---

### Analyze URLs

#### `POST /api/analyze-urls`

Analyze readability of multiple article URLs.

**Request Body:**
```json
{
  "urls": [
    "https://www.example.com/article1",
    "https://www.example.com/article2"
  ]
}
```

**Request Schema:**
- `urls` (array of strings, required)
  - Minimum: 1 URL
  - Maximum: 200 URLs
  - Must be valid HTTP/HTTPS URLs

**Response:**
```json
{
  "results": [
    {
      "url": "https://www.example.com/article1",
      "title": "Article Title",
      "extraction_success": true,
      "metrics": {
        "flesch_kincaid_grade": 10.3,
        "smog": 11.2,
        "coleman_liau": 10.8,
        "ari": 10.5,
        "consensus": 10.7,
        "word_count": 847,
        "sentence_count": 42
      },
      "error": null
    },
    {
      "url": "https://www.example.com/article2",
      "title": null,
      "extraction_success": false,
      "metrics": null,
      "error": "Failed to extract text"
    }
  ],
  "summary": {
    "total_urls": 2,
    "successful": 1,
    "failed": 1,
    "average_grade_level": 10.7
  }
}
```

**Response Schema:**

`results` (array): Analysis results for each URL
- `url` (string): Article URL
- `title` (string|null): Extracted article title
- `extraction_success` (boolean): Whether extraction succeeded
- `metrics` (object|null): Readability metrics (if successful)
  - `flesch_kincaid_grade` (float): Flesch-Kincaid Grade Level
  - `smog` (float): SMOG Index
  - `coleman_liau` (float): Coleman-Liau Index
  - `ari` (float): Automated Readability Index
  - `consensus` (float): Average of all 4 metrics (recommended)
  - `word_count` (integer): Total words
  - `sentence_count` (integer): Total sentences
- `error` (string|null): Error message (if failed)

`summary` (object): Summary statistics
- `total_urls` (integer): Total URLs processed
- `successful` (integer): Successfully analyzed
- `failed` (integer): Failed analyses
- `average_grade_level` (float|null): Average consensus grade (successful only)

**Status Codes:**
- `200 OK` - Request processed successfully
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

**Performance:**
- Processing time: ~2 seconds per article
- Batch of 100 URLs: ~3 minutes (sequential processing)

**Error Handling:**
- Partial failures are included in results
- Failed URLs don't prevent processing of other URLs
- Average grade level excludes failed URLs

---

## Readability Metrics

### Grade Level Interpretation

| Grade Level | Reading Level | Target Audience |
|-------------|---------------|-----------------|
| 0-5 | Elementary | Children |
| 6-8 | Middle School | Pre-teens |
| 9-12 | High School | Teenagers |
| 13-16 | College | Adults |
| 17+ | Graduate | Academics |

### Metric Descriptions

**Flesch-Kincaid Grade Level** (Primary)
- Most widely recognized readability formula
- Based on sentence length and syllables per word
- U.S. school grade level required to understand text

**SMOG Index**
- Simple Measure of Gobbledygook
- Focuses on polysyllabic words
- Designed for health education materials
- Best for educational content

**Coleman-Liau Index**
- Based on characters per word and words per sentence
- Doesn't require syllable counting
- Good for technical content

**Automated Readability Index (ARI)**
- Uses characters per word and words per sentence
- Quick estimate of grade level
- Originally developed for real-time monitoring

**Consensus Grade Level** (Recommended)
- Average of all four metrics
- Provides balanced, reliable estimate
- Use this for reporting and comparisons

---

## Examples

### Analyze Single URL

```bash
curl -X POST "http://localhost:8000/api/analyze-urls" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://www.investopedia.com/terms/c/compoundinterest.asp"]}'
```

### Analyze Multiple URLs

```bash
curl -X POST "http://localhost:8000/api/analyze-urls" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://www.nytimes.com/2024/01/15/business/economy/inflation.html",
      "https://www.wsj.com/economy/jobs/employment-labor-market",
      "https://www.investopedia.com/terms/i/inflation.asp"
    ]
  }'
```

### Python Client Example

```python
import requests

url = "http://localhost:8000/api/analyze-urls"

payload = {
    "urls": [
        "https://www.example.com/article1",
        "https://www.example.com/article2"
    ]
}

response = requests.post(url, json=payload)
data = response.json()

print(f"Analyzed {data['summary']['total_urls']} URLs")
print(f"Success rate: {data['summary']['successful']}/{data['summary']['total_urls']}")
print(f"Average grade level: {data['summary']['average_grade_level']}")

for result in data['results']:
    if result['extraction_success']:
        print(f"\n{result['title']}")
        print(f"  Consensus grade: {result['metrics']['consensus']}")
        print(f"  Word count: {result['metrics']['word_count']}")
    else:
        print(f"\nFailed: {result['url']}")
        print(f"  Error: {result['error']}")
```

### JavaScript/TypeScript Example

```typescript
const analyzeUrls = async (urls: string[]) => {
  const response = await fetch('http://localhost:8000/api/analyze-urls', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ urls }),
  });

  if (!response.ok) {
    throw new Error('Analysis failed');
  }

  return await response.json();
};

// Usage
const results = await analyzeUrls([
  'https://www.example.com/article1',
  'https://www.example.com/article2',
]);

console.log(`Average grade: ${results.summary.average_grade_level}`);
```

---

## Error Responses

### Validation Error (422)

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "urls"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

### Common Validation Errors

- **Empty URL list**: Must provide at least 1 URL
- **Too many URLs**: Maximum 200 URLs per request
- **Invalid URL format**: URLs must be valid HTTP/HTTPS

---

## Rate Limiting

Currently no rate limiting is implemented (internal tool).

For production deployment, consider:
- Rate limiting by IP
- Request size limits (currently 200 URLs max)
- Timeout configuration for long-running requests

---

## CORS Configuration

CORS is configured to allow requests from:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternative dev server)

Configure additional origins in `.env`:
```
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://your-domain.com
```

---

## Configuration

Environment variables (see `.env.example`):

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Text Extraction
EXTRACTION_TIMEOUT=10          # Seconds
MAX_CONCURRENT_REQUESTS=10     # Future: async processing
MAX_RETRIES=3                  # Retry attempts

# Logging
LOG_LEVEL=INFO
```

---

## Development

### Start Server

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### Run Tests

```bash
# All API tests
pytest app/tests/test_api.py -v

# Specific test class
pytest app/tests/test_api.py::TestAnalyzeUrlsEndpoint -v

# With coverage
pytest app/tests/test_api.py --cov=app.api
```

### View API Docs

Once server is running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Troubleshooting

### "Failed to extract text"
- Verify URL is accessible
- Check if site blocks automated access
- Try with different article URLs
- Check extraction timeout setting

### "Analysis error"
- Rare - usually indicates malformed text
- Check logs for details
- Report if persistent

### Slow processing
- Normal: ~2 seconds per article
- 100 URLs takes ~3 minutes
- Future: async batch processing will improve speed

### All URLs failing
- Check network connectivity
- Verify URLs are valid and accessible
- Check if sites are rate limiting

---

## Future Enhancements

Planned for future sprints:
- True async batch processing (parallel URL fetching)
- WebSocket support for real-time progress
- Result caching
- PDF article support
- Custom extraction rules per domain
