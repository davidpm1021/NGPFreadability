"""Pydantic schemas for request/response models"""
from typing import Optional
from pydantic import BaseModel, HttpUrl, Field


class ExtractionRequest(BaseModel):
    """Request model for text extraction from a URL"""
    url: HttpUrl


class ExtractionResult(BaseModel):
    """Result of text extraction from a URL"""
    url: str
    text: Optional[str] = None
    title: Optional[str] = None
    success: bool
    error: Optional[str] = None
    extraction_method: Optional[str] = None  # 'trafilatura' or 'readability-lxml'


class ExtractionError(BaseModel):
    """Error details for failed extraction"""
    url: str
    error_type: str
    error_message: str
    timestamp: str


class ReadabilityMetrics(BaseModel):
    """Readability metrics for analyzed text"""
    flesch_kincaid_grade: float = Field(..., description="Flesch-Kincaid Grade Level")
    smog: float = Field(..., description="SMOG Index (Simple Measure of Gobbledygook)")
    coleman_liau: float = Field(..., description="Coleman-Liau Index")
    ari: float = Field(..., description="Automated Readability Index")
    consensus: float = Field(..., description="Consensus grade level (average of all metrics)")
    word_count: int = Field(..., description="Total number of words")
    sentence_count: int = Field(..., description="Total number of sentences")


class UrlAnalysisRequest(BaseModel):
    """Request model for analyzing multiple URLs"""
    urls: list[str] = Field(..., min_length=1, max_length=200, description="List of URLs to analyze")

    class Config:
        json_schema_extra = {
            "example": {
                "urls": [
                    "https://www.example.com/article1",
                    "https://www.example.com/article2"
                ]
            }
        }


class ArticleAnalysis(BaseModel):
    """Complete analysis result for a single article"""
    url: str = Field(..., description="Article URL")
    title: Optional[str] = Field(None, description="Extracted article title")
    extraction_success: bool = Field(..., description="Whether text extraction succeeded")
    metrics: Optional[ReadabilityMetrics] = Field(None, description="Readability metrics (if extraction succeeded)")
    error: Optional[str] = Field(None, description="Error message (if extraction or analysis failed)")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.example.com/article",
                "title": "Article Title",
                "extraction_success": True,
                "metrics": {
                    "flesch_kincaid_grade": 10.3,
                    "smog": 11.2,
                    "coleman_liau": 10.8,
                    "ari": 10.5,
                    "consensus": 10.7,
                    "word_count": 847,
                    "sentence_count": 42
                },
                "error": None
            }
        }


class AnalysisSummary(BaseModel):
    """Summary statistics for batch analysis"""
    total_urls: int = Field(..., description="Total number of URLs processed")
    successful: int = Field(..., description="Number of successful analyses")
    failed: int = Field(..., description="Number of failed analyses")
    average_grade_level: Optional[float] = Field(None, description="Average consensus grade level (successful only)")

    class Config:
        json_schema_extra = {
            "example": {
                "total_urls": 87,
                "successful": 84,
                "failed": 3,
                "average_grade_level": 10.8
            }
        }


class BatchAnalysisResponse(BaseModel):
    """Response model for batch URL analysis"""
    results: list[ArticleAnalysis] = Field(..., description="Analysis results for each URL")
    summary: AnalysisSummary = Field(..., description="Summary statistics")

    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "url": "https://www.example.com/article1",
                        "title": "Article 1",
                        "extraction_success": True,
                        "metrics": {
                            "flesch_kincaid_grade": 10.3,
                            "smog": 11.2,
                            "coleman_liau": 10.8,
                            "ari": 10.5,
                            "consensus": 10.7,
                            "word_count": 847,
                            "sentence_count": 42
                        },
                        "error": None
                    }
                ],
                "summary": {
                    "total_urls": 1,
                    "successful": 1,
                    "failed": 0,
                    "average_grade_level": 10.7
                }
            }
        }
