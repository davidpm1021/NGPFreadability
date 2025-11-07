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
