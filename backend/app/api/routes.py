"""API route handlers"""
import logging
import time
import uuid
import signal
from typing import Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError, as_completed

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    UrlAnalysisRequest,
    BatchAnalysisResponse,
    ArticleAnalysis,
    AnalysisSummary,
)
from app.services.extraction import extract_text, should_skip_url, clean_url
from app.services.readability import analyze_text

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analysis"])

# In-memory progress tracking (simple solution for now)
_progress_tracker: Dict[str, Dict[str, Any]] = {}


def process_url(url: str) -> Dict[str, Any]:
    """
    Process a single URL: extract text and analyze readability.

    Args:
        url: URL to process

    Returns:
        Dictionary with analysis results
    """
    try:
        # Step 1: Extract text from URL
        extraction_result = extract_text(url)

        if not extraction_result.success or not extraction_result.text:
            return {
                "url": url,
                "title": extraction_result.title,
                "extraction_success": False,
                "metrics": None,
                "error": extraction_result.error or "Failed to extract text"
            }

        # Step 2: Analyze readability
        try:
            metrics = analyze_text(extraction_result.text)

            return {
                "url": url,
                "title": extraction_result.title,
                "extraction_success": True,
                "metrics": {
                    "flesch_kincaid_grade": metrics.flesch_kincaid_grade,
                    "smog": metrics.smog,
                    "coleman_liau": metrics.coleman_liau,
                    "ari": metrics.ari,
                    "consensus": metrics.consensus,
                    "word_count": metrics.word_count,
                    "sentence_count": metrics.sentence_count,
                },
                "error": None
            }
        except Exception as e:
            logger.error(f"Error analyzing text for {url}: {e}")
            return {
                "url": url,
                "title": extraction_result.title,
                "extraction_success": False,
                "metrics": None,
                "error": f"Analysis error: {str(e)}"
            }

    except Exception as e:
        logger.error(f"Error processing {url}: {e}")
        return {
            "url": url,
            "title": None,
            "extraction_success": False,
            "metrics": None,
            "error": f"Processing error: {str(e)}"
        }


@router.get("/progress/{request_id}")
async def get_progress(request_id: str) -> Dict[str, Any]:
    """Get progress for a running analysis request"""
    if request_id not in _progress_tracker:
        raise HTTPException(status_code=404, detail="Request not found")
    return _progress_tracker[request_id]


@router.get("/progress")
async def get_latest_progress() -> Optional[Dict[str, Any]]:
    """Get progress for the most recent active request"""
    # Return the most recent active request
    active_requests = [
        p for p in _progress_tracker.values() 
        if p.get("status") == "processing"
    ]
    if not active_requests:
        return None
    # Return the most recent one (by started_at)
    return max(active_requests, key=lambda x: x.get("started_at", ""))


@router.post("/analyze-urls", response_model=BatchAnalysisResponse)
async def analyze_urls(request: UrlAnalysisRequest) -> BatchAnalysisResponse:
    """
    Analyze readability of multiple URLs.

    Extracts text from each URL and calculates readability metrics:
    - Flesch-Kincaid Grade Level
    - SMOG Index
    - Coleman-Liau Index
    - Automated Readability Index (ARI)
    - Consensus grade level (average)
    - Word and sentence counts

    **Process:**
    1. Extract text from each URL (Trafilatura with readability-lxml fallback)
    2. Calculate readability metrics for successfully extracted text
    3. Return results with summary statistics

    **Performance:**
    - Processes URLs CONCURRENTLY with 10 parallel workers
    - Target: <2 seconds per article (effectively ~0.2s per URL throughput)
    - Handles up to 200 URLs per request

    **Success Rate:**
    - Expected: >90% extraction success on news articles
    - Failed extractions are included in results with error messages

    Args:
        request: UrlAnalysisRequest with list of URLs

    Returns:
        BatchAnalysisResponse with results and summary

    Raises:
        HTTPException: If request validation fails
    """
    logger.info(f"Received request to analyze {len(request.urls)} URLs")
    logger.debug(f"URLs: {request.urls[:5]}..." if len(request.urls) > 5 else f"URLs: {request.urls}")

    # Create progress tracker entry
    request_id = str(uuid.uuid4())
    start_time = time.time()
    _progress_tracker[request_id] = {
        "request_id": request_id,
        "total_urls": len(request.urls),
        "processed": 0,
        "successful": 0,
        "failed": 0,
        "current_url": None,
        "started_at": datetime.now().isoformat(),
        "status": "processing",
    }

    try:
        # Filter out URLs that should be silently skipped (YouTube, EdPuzzle, etc.)
        urls_to_process = []
        for url in request.urls:
            cleaned = clean_url(url)
            if not should_skip_url(cleaned):
                urls_to_process.append(cleaned)
            else:
                logger.info(f"Silently skipping URL: {cleaned}")

        logger.info(f"Processing {len(urls_to_process)} URLs after filtering")
        _progress_tracker[request_id]["total_urls"] = len(urls_to_process)

        # Handle empty URL list (all filtered out)
        if not urls_to_process:
            logger.info("All URLs were filtered out - returning empty result")
            _progress_tracker[request_id]["status"] = "completed"
            return BatchAnalysisResponse(
                results=[],
                summary=AnalysisSummary(
                    total_urls=0,
                    successful=0,
                    failed=0,
                    average_grade_level=None
                )
            )

        # Process URLs CONCURRENTLY for much better performance
        # Use 10 concurrent workers to process ~10x faster
        max_workers = 10
        max_url_timeout = 30
        results = []
        url_to_result = {}  # Map URL to result for ordered output

        logger.info(f"🚀 Starting concurrent processing with {max_workers} workers")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all URLs to the executor
            future_to_url = {
                executor.submit(process_url, url): url
                for url in urls_to_process
            }

            processed_count = 0
            progress_interval = max(1, min(10, len(urls_to_process) // 20))

            # Process results as they complete
            for future in as_completed(future_to_url, timeout=max_url_timeout * len(urls_to_process)):
                url = future_to_url[future]
                processed_count += 1
                url_success = False

                try:
                    result = future.result(timeout=max_url_timeout)
                    url_to_result[url] = result
                    url_success = result.get("extraction_success", False)
                except FutureTimeoutError:
                    logger.error(f"URL timed out after {max_url_timeout}s: {url[:80]}...")
                    url_to_result[url] = {
                        "url": url,
                        "title": None,
                        "extraction_success": False,
                        "metrics": None,
                        "error": f"Processing timeout after {max_url_timeout} seconds"
                    }
                except Exception as e:
                    logger.error(f"Error processing URL: {url[:80]}... - {e}")
                    url_to_result[url] = {
                        "url": url,
                        "title": None,
                        "extraction_success": False,
                        "metrics": None,
                        "error": f"Processing error: {str(e)}"
                    }

                # Update progress tracker
                _progress_tracker[request_id]["processed"] = processed_count
                _progress_tracker[request_id]["current_url"] = url[:100] + "..." if len(url) > 100 else url

                if url_success:
                    _progress_tracker[request_id]["successful"] += 1
                else:
                    _progress_tracker[request_id]["failed"] += 1

                # Log progress periodically
                if processed_count == 1 or processed_count == len(urls_to_process) or processed_count % progress_interval == 0:
                    elapsed = time.time() - start_time
                    avg_time_per_url = elapsed / processed_count if processed_count > 0 else 0
                    remaining = (len(urls_to_process) - processed_count) * avg_time_per_url / max_workers
                    pct = processed_count * 100 // len(urls_to_process)

                    logger.info(
                        f"⚡ Progress: {processed_count}/{len(urls_to_process)} ({pct}%) - "
                        f"Elapsed: {elapsed:.1f}s, Est. remaining: {remaining:.1f}s"
                    )

                    _progress_tracker[request_id]["elapsed_seconds"] = round(elapsed, 1)
                    _progress_tracker[request_id]["avg_time_per_url"] = round(avg_time_per_url, 2)
                    _progress_tracker[request_id]["estimated_remaining_seconds"] = round(remaining, 1)

                # Heartbeat every 20 URLs
                if processed_count % 20 == 0:
                    elapsed = time.time() - start_time
                    logger.info(
                        f"💓 Heartbeat: {processed_count}/{len(urls_to_process)} "
                        f"({processed_count*100//len(urls_to_process)}%) in {elapsed:.1f}s"
                    )

        # Build results in original URL order
        results = [url_to_result[url] for url in urls_to_process]

        # Calculate summary statistics
        successful = [r for r in results if r["extraction_success"]]
        failed = [r for r in results if not r["extraction_success"]]

        # Calculate average grade level (only from successful analyses)
        if successful:
            grade_levels = [r["metrics"]["consensus"] for r in successful]
            average_grade = round(sum(grade_levels) / len(grade_levels), 1)
        else:
            average_grade = None

        # Build response
        response = BatchAnalysisResponse(
            results=[
                ArticleAnalysis(
                    url=r["url"],
                    title=r["title"],
                    extraction_success=r["extraction_success"],
                    metrics=r["metrics"],
                    error=r["error"]
                )
                for r in results
            ],
            summary=AnalysisSummary(
                total_urls=len(results),
                successful=len(successful),
                failed=len(failed),
                average_grade_level=average_grade
            )
        )

        total_time = time.time() - start_time
        avg_time = total_time / len(urls_to_process) if urls_to_process else 0

        # Update final progress
        _progress_tracker[request_id]["status"] = "completed"
        _progress_tracker[request_id]["completed_at"] = datetime.now().isoformat()
        _progress_tracker[request_id]["total_seconds"] = round(total_time, 1)

        logger.info(
            f"✅ Analysis complete: {len(successful)} successful, "
            f"{len(failed)} failed, avg grade: {average_grade} - "
            f"Total time: {total_time:.1f}s ({avg_time:.2f}s per URL)"
        )

        return response
    except Exception as e:
        _progress_tracker[request_id]["status"] = "error"
        _progress_tracker[request_id]["error"] = str(e)
        raise
