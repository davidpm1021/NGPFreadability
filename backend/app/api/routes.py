"""API route handlers"""
import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    UrlAnalysisRequest,
    BatchAnalysisResponse,
    ArticleAnalysis,
    AnalysisSummary,
)
from app.services.extraction import extract_text
from app.services.readability import analyze_text

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analysis"])


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
    - Processes URLs sequentially (async batch processing in future sprint)
    - Target: <2 seconds per article
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
    logger.info(f"Analyzing {len(request.urls)} URLs")

    # Process each URL
    results = []
    for url in request.urls:
        result = process_url(url)
        results.append(result)

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

    logger.info(
        f"Analysis complete: {len(successful)} successful, "
        f"{len(failed)} failed, avg grade: {average_grade}"
    )

    return response
