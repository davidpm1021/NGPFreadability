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
