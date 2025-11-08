"""Text extraction service using Trafilatura and readability-lxml"""
import asyncio
import logging
import re
from typing import Optional, List
from urllib.parse import urlparse

import aiohttp
import requests
from trafilatura import fetch_url, extract
from readability import Document

from app.models.schemas import ExtractionResult
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def clean_url(url: str) -> str:
    """
    Clean URL by removing trailing punctuation and whitespace.

    Args:
        url: URL string to clean

    Returns:
        Cleaned URL string
    """
    if not url:
        return url

    # Strip whitespace
    url = url.strip()

    # Remove trailing punctuation that might be from markdown/text
    # Common: ), ], ., ,, ;
    while url and url[-1] in '()[].,;':
        url = url[:-1]

    return url


def should_skip_url(url: str) -> bool:
    """
    Check if URL should be silently skipped (not shown in results).

    Args:
        url: URL to check

    Returns:
        True if URL should be skipped, False otherwise
    """
    try:
        parsed = urlparse(url)
        path = parsed.path.lower()

        # Skip YouTube URLs silently
        if 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc:
            return True

        # Skip EdPuzzle URLs silently
        if 'edpuzzle.com' in parsed.netloc:
            return True

        # Skip Instagram posts silently
        if 'instagram.com' in parsed.netloc:
            return True

        # Skip direct image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp']
        if any(path.endswith(ext) for ext in image_extensions):
            return True

        # Skip infographic/data viz platforms
        infographic_domains = ['infogram.com', 'datawrapper.de', 'tableau.com']
        if any(domain in parsed.netloc for domain in infographic_domains):
            return True

        return False

    except Exception:
        return False


def is_article_url(url: str) -> tuple[bool, str]:
    """
    Check if URL is likely an article (not homepage, embed, category page, etc.)

    Args:
        url: URL to check

    Returns:
        Tuple of (is_valid, reason_if_invalid)
    """
    try:
        parsed = urlparse(url)
        path = parsed.path.rstrip('/')

        # Skip video embeds from other platforms
        if any(platform in parsed.netloc for platform in ['vimeo.com', 'dailymotion.com']):
            return False, "Video content cannot be analyzed"

        # Skip homepages (URLs with no path or just '/')
        if not path or path == '':
            return False, "Homepage URLs cannot be analyzed - please use article URLs"

        # Skip category/archive pages (URLs ending in category names)
        # Only block if it's JUST the category with nothing after
        path_segments = [p for p in path.split('/') if p]

        # Very limited category blocking - only obvious ones
        category_keywords = ['blog', 'category', 'tag', 'archive', 'author', 'topic']
        if len(path_segments) == 1 and path_segments[0] in category_keywords:
            return False, "Category/archive pages cannot be analyzed - please use specific article URLs"

        # Allow everything else - let the extraction fail if it's not an article
        return True, ""

    except Exception as e:
        return False, f"Invalid URL: {str(e)}"


def validate_url(url: str) -> bool:
    """
    Validate that a URL is well-formed and uses HTTP/HTTPS protocol.

    Args:
        url: URL string to validate

    Returns:
        True if URL is valid, False otherwise
    """
    try:
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https') and bool(parsed.netloc)
    except Exception:
        return False


def clean_extracted_text(text: str) -> str:
    """
    Clean extracted text by removing common artifacts and noise.

    Args:
        text: Raw extracted text

    Returns:
        Cleaned text with artifacts removed
    """
    if not text:
        return text

    # Remove photo/video credits (AP Photo, Getty Images, etc.)
    text = re.sub(r'\((?:AP|Getty|Reuters|AFP)\s+(?:Photo|Video|Image)[^)]*\)', '', text)

    # Remove standalone photo credit patterns
    text = re.sub(r'Photo by:?\s+[^\n]+', '', text)
    text = re.sub(r'Image credit:?\s+[^\n]+', '', text, flags=re.IGNORECASE)

    # Remove video/audio credits (more comprehensive)
    text = re.sub(r'\((?:AP\s+)?(?:Video|Production)(?:\s+by)?:?\s+[^)]+\)', '', text, flags=re.IGNORECASE)

    # Remove photo caption sentences - multiple aggressive patterns
    # Pattern 1: Any sentence with Traveler/Traveller + action + location + date
    text = re.sub(r'(?:Traveler|Traveller)s?\s+(?:head|walk|stand|wait|move|sit|line)[^.]*?\.', '', text, flags=re.IGNORECASE)

    # Pattern 2: Generic caption pattern - [People/things] [action] [preposition] [location] [date]
    text = re.sub(r'(?:People|Passengers|Crowd|Staff|Workers)[^.]*?(?:at|in|near)\s+[^.]*?(?:Airport|terminal|checkpoint)[^.]*?\.', '', text, flags=re.IGNORECASE)

    # Pattern 3: Just date/location descriptions
    text = re.sub(r'[^.]*?(?:Nov\.|Jan\.|Feb\.|Mar\.|Apr\.|May|Jun\.|Jul\.|Aug\.|Sep\.|Oct\.|Dec\.)\s+\d+,\s+2\d{3}[^.]*?\.', '', text, flags=re.IGNORECASE)

    # Pattern 4: Orphaned location/date fragments (from partially removed captions)
    text = re.sub(r'^\s*\d+,\s+2\d{3}.*$', '', text, flags=re.MULTILINE)

    # Remove "Planes/Aircraft are seen..." captions
    text = re.sub(r'Planes?\s+(?:are\s+)?seen\s+at[^.]+\.', '', text, flags=re.IGNORECASE)

    # Remove social media share buttons text
    text = re.sub(r'(?:Share|Tweet|Email|Print)\s+(?:this|on)\s+(?:Facebook|Twitter|LinkedIn|Email)?', '', text, flags=re.IGNORECASE)

    # Remove "Read more" / "Continue reading" links
    text = re.sub(r'(?:Read more|Continue reading|Click here)[^\n]*', '', text, flags=re.IGNORECASE)

    # Remove advertisement markers
    text = re.sub(r'(?:Advertisement|ADVERTISEMENT|Sponsored)', '', text)

    # Remove multiple author attribution patterns
    text = re.sub(r'Associated Press journalists?\s+[^.]+contributed\.?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'___+', '', text)  # Remove horizontal lines often used before credits

    # Remove navigation menu content (common in blog sites)
    # Pattern: Lists of category links (Activities, Advocacy, Behavioral Economics, etc.)
    lines = text.split('\n')
    filtered_lines = []
    consecutive_short_lines = 0
    skip_mode = False

    for line in lines:
        stripped = line.strip()

        # Detect navigation menus: 3+ consecutive short lines (< 30 chars, capitalized)
        if len(stripped) < 30 and stripped and stripped[0].isupper() and not stripped.endswith('.'):
            consecutive_short_lines += 1
            if consecutive_short_lines >= 3:
                skip_mode = True
            continue
        elif skip_mode and len(stripped) < 30:
            # Keep skipping short lines in menu
            continue
        else:
            # Reset when we hit normal content
            consecutive_short_lines = 0
            skip_mode = False
            filtered_lines.append(line)

    text = '\n'.join(filtered_lines)

    # Fix common encoding issues
    text = text.replace('�', "'")  # Replace common apostrophe encoding error
    text = text.replace('–', '-')  # Replace en-dash
    text = text.replace('—', '-')  # Replace em-dash
    text = text.replace('"', '"').replace('"', '"')  # Replace smart quotes
    text = text.replace(''', "'").replace(''', "'")  # Replace smart apostrophes

    # Remove repeated consecutive lines and paragraphs (more aggressive)
    lines = text.split('\n')
    cleaned_lines = []
    seen_paragraphs = set()
    prev_line = None

    for line in lines:
        stripped = line.strip()

        # Skip empty lines that would create more than 2 consecutive blank lines
        if not stripped:
            if not cleaned_lines or cleaned_lines[-1].strip():
                cleaned_lines.append(line)
            prev_line = None
            continue

        # Skip exact duplicate consecutive lines
        if stripped == prev_line:
            continue

        # Skip duplicate paragraphs (if we've seen this exact paragraph before)
        if len(stripped) > 50:  # Only check substantial paragraphs
            if stripped in seen_paragraphs:
                continue
            seen_paragraphs.add(stripped)

        cleaned_lines.append(line)
        prev_line = stripped

    text = '\n'.join(cleaned_lines)

    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 consecutive newlines
    text = re.sub(r' {2,}', ' ', text)  # Multiple spaces to single space
    text = re.sub(r'\t+', ' ', text)  # Tabs to single space

    # Try to detect and remove repeated lead/summary at the start
    # Often news sites repeat the headline and first few paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    if len(paragraphs) > 5:
        # Check if first few paragraphs appear again later
        first_three = paragraphs[:3]
        # Look for the actual article start (where unique content begins)
        for i in range(3, min(10, len(paragraphs))):
            # If we find a substantial paragraph that looks like article content
            # (contains transition words, quotes, or is significantly longer)
            if len(paragraphs[i]) > 200 and (
                'said' in paragraphs[i].lower() or
                '"' in paragraphs[i] or
                any(word in paragraphs[i].lower() for word in ['however', 'but', 'while', 'though', 'anxious', 'plenty'])
            ):
                # Check if this paragraph was already seen in first 3
                if paragraphs[i] not in first_three:
                    # Likely found the real article start
                    # Remove lead paragraphs if they seem repetitive
                    if any(para in ' '.join(paragraphs[i:]) for para in first_three):
                        paragraphs = paragraphs[i:]
                        break

        text = '\n\n'.join(paragraphs)

    return text.strip()


def extract_with_trafilatura(
    url: str,
    timeout: Optional[int] = None
) -> Optional[str]:
    """
    Extract text from URL using Trafilatura.

    Args:
        url: URL to extract text from
        timeout: Optional timeout in seconds

    Returns:
        Extracted text or None if extraction fails
    """
    try:
        # Use configured timeout or default
        timeout = timeout or settings.extraction_timeout

        # Fetch the URL content
        downloaded = fetch_url(url)
        if not downloaded:
            logger.warning(f"Trafilatura: Failed to fetch {url}")
            return None

        # Extract text with Trafilatura
        text = extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            no_fallback=False
        )

        if text:
            logger.info(f"Trafilatura: Successfully extracted from {url}")
            return text
        else:
            logger.warning(f"Trafilatura: No text extracted from {url}")
            return None

    except TimeoutError as e:
        logger.error(f"Trafilatura: Timeout extracting {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Trafilatura: Error extracting {url}: {e}")
        return None


def extract_with_readability(
    url: str,
    timeout: Optional[int] = None
) -> Optional[str]:
    """
    Extract text from URL using readability-lxml as fallback.

    Args:
        url: URL to extract text from
        timeout: Optional timeout in seconds

    Returns:
        Extracted text or None if extraction fails
    """
    try:
        timeout = timeout or settings.extraction_timeout

        # Fetch the URL
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

        # Extract with readability
        doc = Document(response.content)
        title = doc.title()
        summary = doc.summary()

        # Strip HTML tags from summary
        from html import unescape
        import re
        text = re.sub('<[^<]+?>', '', summary)
        text = unescape(text).strip()

        if text:
            logger.info(f"Readability: Successfully extracted from {url}")
            return text
        else:
            logger.warning(f"Readability: No text extracted from {url}")
            return None

    except Exception as e:
        logger.error(f"Readability: Error extracting {url}: {e}")
        return None


def extract_text(
    url: str,
    timeout: Optional[int] = None
) -> ExtractionResult:
    """
    Extract text from URL using Trafilatura with readability-lxml fallback.

    Args:
        url: URL to extract text from
        timeout: Optional timeout in seconds

    Returns:
        ExtractionResult with success status and extracted text
    """
    # Clean URL first (remove trailing punctuation)
    url = clean_url(url)

    # Validate URL format
    if not validate_url(url):
        return ExtractionResult(
            url=url,
            success=False,
            error="Invalid URL format"
        )

    # Check if URL is likely an article
    is_valid_article, reason = is_article_url(url)
    if not is_valid_article:
        return ExtractionResult(
            url=url,
            success=False,
            error=reason
        )

    # Try Trafilatura first
    try:
        text = extract_with_trafilatura(url, timeout)
        if text:
            cleaned_text = clean_extracted_text(text)
            return ExtractionResult(
                url=url,
                text=cleaned_text,
                success=True,
                extraction_method="trafilatura"
            )
    except TimeoutError:
        return ExtractionResult(
            url=url,
            success=False,
            error="Request timeout"
        )

    # Fallback to readability-lxml
    logger.info(f"Falling back to readability-lxml for {url}")
    text = extract_with_readability(url, timeout)
    if text:
        cleaned_text = clean_extracted_text(text)
        return ExtractionResult(
            url=url,
            text=cleaned_text,
            success=True,
            extraction_method="readability-lxml"
        )

    # Both methods failed
    return ExtractionResult(
        url=url,
        success=False,
        error="Failed to extract text with both Trafilatura and readability-lxml"
    )


async def fetch_url_async(
    session: aiohttp.ClientSession,
    url: str,
    timeout: Optional[int] = None
) -> Optional[str]:
    """
    Fetch URL content asynchronously using aiohttp.

    Args:
        session: aiohttp ClientSession
        url: URL to fetch
        timeout: Optional timeout in seconds

    Returns:
        HTML content or None if fetch fails
    """
    try:
        timeout_config = aiohttp.ClientTimeout(
            total=timeout or settings.extraction_timeout
        )

        async with session.get(url, timeout=timeout_config) as response:
            if response.status == 200:
                return await response.text()
            else:
                logger.warning(f"HTTP {response.status} for {url}")
                return None

    except asyncio.TimeoutError:
        logger.error(f"Timeout fetching {url}")
        return None
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None


async def fetch_with_retry(
    session: Optional[aiohttp.ClientSession],
    url: str,
    max_retries: Optional[int] = None,
    timeout: Optional[int] = None
) -> Optional[str]:
    """
    Fetch URL with retry logic and exponential backoff.

    Args:
        session: aiohttp ClientSession
        url: URL to fetch
        max_retries: Maximum number of retry attempts
        timeout: Optional timeout in seconds

    Returns:
        HTML content or None if all retries fail
    """
    max_retries = max_retries or settings.max_retries

    for attempt in range(max_retries):
        try:
            result = await fetch_url_async(session, url, timeout)
            if result:
                return result
        except Exception as e:
            if attempt < max_retries - 1:
                # Exponential backoff: 1s, 2s, 4s, etc.
                delay = 2 ** attempt
                logger.info(f"Retry {attempt + 1}/{max_retries} for {url} after {delay}s")
                await asyncio.sleep(delay)
            else:
                logger.error(f"All retries failed for {url}: {e}")

    return None


async def fetch_multiple_urls(
    urls: List[str],
    max_concurrent: Optional[int] = None,
    timeout: Optional[int] = None
) -> List[Optional[str]]:
    """
    Fetch multiple URLs concurrently with rate limiting.

    Args:
        urls: List of URLs to fetch
        max_concurrent: Maximum number of concurrent requests
        timeout: Optional timeout in seconds

    Returns:
        List of HTML content (None for failed fetches)
    """
    max_concurrent = max_concurrent or settings.max_concurrent_requests
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_semaphore(session: aiohttp.ClientSession, url: str):
        async with semaphore:
            return await fetch_with_retry(session, url, timeout=timeout)

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_with_semaphore(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to None
        return [r if not isinstance(r, Exception) else None for r in results]


async def extract_multiple_urls(
    urls: List[str],
    max_concurrent: Optional[int] = None,
    timeout: Optional[int] = None
) -> List[ExtractionResult]:
    """
    Extract text from multiple URLs concurrently.

    Args:
        urls: List of URLs to extract from
        max_concurrent: Maximum number of concurrent requests
        timeout: Optional timeout in seconds

    Returns:
        List of ExtractionResult objects
    """
    # First, fetch all URLs concurrently
    html_contents = await fetch_multiple_urls(urls, max_concurrent, timeout)

    # Then extract text from each (this is CPU-bound, so we do it synchronously)
    results = []
    for url, html in zip(urls, html_contents):
        if not validate_url(url):
            results.append(ExtractionResult(
                url=url,
                success=False,
                error="Invalid URL format"
            ))
            continue

        if not html:
            results.append(ExtractionResult(
                url=url,
                success=False,
                error="Failed to fetch URL"
            ))
            continue

        # Try extracting with Trafilatura
        try:
            text = extract(
                html,
                include_comments=False,
                include_tables=False,
                no_fallback=False
            )

            if text:
                results.append(ExtractionResult(
                    url=url,
                    text=text,
                    success=True,
                    extraction_method="trafilatura"
                ))
            else:
                # Try readability as fallback
                try:
                    doc = Document(html)
                    summary = doc.summary()

                    from html import unescape
                    import re
                    text = re.sub('<[^<]+?>', '', summary)
                    text = unescape(text).strip()

                    if text:
                        results.append(ExtractionResult(
                            url=url,
                            text=text,
                            success=True,
                            extraction_method="readability-lxml"
                        ))
                    else:
                        results.append(ExtractionResult(
                            url=url,
                            success=False,
                            error="No text extracted"
                        ))
                except Exception as e:
                    results.append(ExtractionResult(
                        url=url,
                        success=False,
                        error=f"Extraction error: {str(e)}"
                    ))
        except Exception as e:
            results.append(ExtractionResult(
                url=url,
                success=False,
                error=f"Extraction error: {str(e)}"
            ))

    return results
