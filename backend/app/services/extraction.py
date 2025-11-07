"""Text extraction service using Trafilatura and readability-lxml"""
import asyncio
import logging
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
    # Validate URL first
    if not validate_url(url):
        return ExtractionResult(
            url=url,
            success=False,
            error="Invalid URL format"
        )

    # Try Trafilatura first
    try:
        text = extract_with_trafilatura(url, timeout)
        if text:
            return ExtractionResult(
                url=url,
                text=text,
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
        return ExtractionResult(
            url=url,
            text=text,
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
