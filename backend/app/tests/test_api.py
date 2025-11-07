"""Tests for API endpoints"""
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import ReadabilityMetrics, ExtractionResult

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint returns status"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert "version" in data

    def test_health_endpoint(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestAnalyzeUrlsEndpoint:
    """Test /api/analyze-urls endpoint"""

    @patch('app.api.routes.process_url')
    def test_analyze_single_url(self, mock_process):
        """Test analyzing a single URL"""
        # Arrange
        mock_process.return_value = {
            "url": "https://example.com/article",
            "title": "Test Article",
            "extraction_success": True,
            "metrics": {
                "flesch_kincaid_grade": 10.5,
                "smog": 11.0,
                "coleman_liau": 10.2,
                "ari": 10.8,
                "consensus": 10.6,
                "word_count": 500,
                "sentence_count": 25
            },
            "error": None
        }

        # Act
        response = client.post(
            "/api/analyze-urls",
            json={"urls": ["https://example.com/article"]}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["extraction_success"] is True
        assert data["results"][0]["metrics"]["consensus"] == 10.6
        assert data["summary"]["total_urls"] == 1
        assert data["summary"]["successful"] == 1
        assert data["summary"]["failed"] == 0

    @patch('app.api.routes.process_url')
    def test_analyze_multiple_urls(self, mock_process):
        """Test analyzing multiple URLs"""
        # Arrange
        mock_process.side_effect = [
            {
                "url": "https://example.com/article1",
                "title": "Article 1",
                "extraction_success": True,
                "metrics": {
                    "flesch_kincaid_grade": 10.0,
                    "smog": 10.5,
                    "coleman_liau": 9.8,
                    "ari": 10.2,
                    "consensus": 10.1,
                    "word_count": 450,
                    "sentence_count": 20
                },
                "error": None
            },
            {
                "url": "https://example.com/article2",
                "title": "Article 2",
                "extraction_success": True,
                "metrics": {
                    "flesch_kincaid_grade": 12.0,
                    "smog": 12.5,
                    "coleman_liau": 11.8,
                    "ari": 12.2,
                    "consensus": 12.1,
                    "word_count": 600,
                    "sentence_count": 30
                },
                "error": None
            }
        ]

        # Act
        response = client.post(
            "/api/analyze-urls",
            json={"urls": [
                "https://example.com/article1",
                "https://example.com/article2"
            ]}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2
        assert data["summary"]["total_urls"] == 2
        assert data["summary"]["successful"] == 2
        assert data["summary"]["failed"] == 0
        # Average of 10.1 and 12.1 = 11.1
        assert data["summary"]["average_grade_level"] == 11.1

    @patch('app.api.routes.process_url')
    def test_analyze_with_partial_failures(self, mock_process):
        """Test analyzing URLs with some failures"""
        # Arrange
        mock_process.side_effect = [
            {
                "url": "https://example.com/success",
                "title": "Success",
                "extraction_success": True,
                "metrics": {
                    "flesch_kincaid_grade": 10.0,
                    "smog": 10.5,
                    "coleman_liau": 9.8,
                    "ari": 10.2,
                    "consensus": 10.1,
                    "word_count": 450,
                    "sentence_count": 20
                },
                "error": None
            },
            {
                "url": "https://example.com/failure",
                "title": None,
                "extraction_success": False,
                "metrics": None,
                "error": "Failed to extract text"
            }
        ]

        # Act
        response = client.post(
            "/api/analyze-urls",
            json={"urls": [
                "https://example.com/success",
                "https://example.com/failure"
            ]}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2
        assert data["results"][0]["extraction_success"] is True
        assert data["results"][1]["extraction_success"] is False
        assert data["summary"]["total_urls"] == 2
        assert data["summary"]["successful"] == 1
        assert data["summary"]["failed"] == 1
        assert data["summary"]["average_grade_level"] == 10.1

    def test_analyze_empty_url_list(self):
        """Test with empty URL list"""
        response = client.post(
            "/api/analyze-urls",
            json={"urls": []}
        )

        # Should return validation error
        assert response.status_code == 422

    def test_analyze_too_many_urls(self):
        """Test with more than 200 URLs"""
        urls = [f"https://example.com/{i}" for i in range(201)]

        response = client.post(
            "/api/analyze-urls",
            json={"urls": urls}
        )

        # Should return validation error
        assert response.status_code == 422

    def test_analyze_invalid_request_format(self):
        """Test with invalid request format"""
        response = client.post(
            "/api/analyze-urls",
            json={"invalid": "data"}
        )

        assert response.status_code == 422

    def test_analyze_missing_request_body(self):
        """Test with missing request body"""
        response = client.post("/api/analyze-urls")

        assert response.status_code == 422


class TestProcessUrl:
    """Test process_url function"""

    @patch('app.api.routes.extract_text')
    @patch('app.api.routes.analyze_text')
    def test_successful_processing(self, mock_analyze, mock_extract):
        """Test successful URL processing"""
        # Arrange
        from app.api.routes import process_url

        mock_extract.return_value = ExtractionResult(
            url="https://example.com/article",
            text="This is test content. It has multiple sentences.",
            title="Test Article",
            success=True,
            extraction_method="trafilatura"
        )

        mock_analyze.return_value = ReadabilityMetrics(
            flesch_kincaid_grade=10.5,
            smog=11.0,
            coleman_liau=10.2,
            ari=10.8,
            consensus=10.6,
            word_count=8,
            sentence_count=2
        )

        # Act
        result = process_url("https://example.com/article")

        # Assert
        assert result["url"] == "https://example.com/article"
        assert result["title"] == "Test Article"
        assert result["extraction_success"] is True
        assert result["metrics"]["consensus"] == 10.6
        assert result["error"] is None

    @patch('app.api.routes.extract_text')
    def test_extraction_failure(self, mock_extract):
        """Test URL processing when extraction fails"""
        # Arrange
        from app.api.routes import process_url

        mock_extract.return_value = ExtractionResult(
            url="https://example.com/article",
            text=None,
            title=None,
            success=False,
            error="Failed to fetch URL"
        )

        # Act
        result = process_url("https://example.com/article")

        # Assert
        assert result["url"] == "https://example.com/article"
        assert result["extraction_success"] is False
        assert result["metrics"] is None
        assert "Failed to fetch URL" in result["error"]

    @patch('app.api.routes.extract_text')
    @patch('app.api.routes.analyze_text')
    def test_analysis_failure(self, mock_analyze, mock_extract):
        """Test URL processing when analysis fails"""
        # Arrange
        from app.api.routes import process_url

        mock_extract.return_value = ExtractionResult(
            url="https://example.com/article",
            text="Short text",
            title="Test",
            success=True,
            extraction_method="trafilatura"
        )

        mock_analyze.side_effect = Exception("Analysis error")

        # Act
        result = process_url("https://example.com/article")

        # Assert
        assert result["url"] == "https://example.com/article"
        assert result["extraction_success"] is False
        assert result["metrics"] is None
        assert "Analysis error" in result["error"]


class TestBatchProcessing:
    """Test batch processing functionality"""

    @patch('app.api.routes.process_url')
    def test_processes_urls_in_order(self, mock_process):
        """Test that URLs are processed in the order provided"""
        # Arrange
        urls = [
            "https://example.com/1",
            "https://example.com/2",
            "https://example.com/3"
        ]

        mock_process.side_effect = [
            {"url": url, "extraction_success": True, "metrics": {
                "flesch_kincaid_grade": 10.0, "smog": 10.0,
                "coleman_liau": 10.0, "ari": 10.0,
                "consensus": 10.0, "word_count": 100,
                "sentence_count": 5
            }, "title": f"Article {i}", "error": None}
            for i, url in enumerate(urls, 1)
        ]

        # Act
        response = client.post(
            "/api/analyze-urls",
            json={"urls": urls}
        )

        # Assert
        data = response.json()
        assert len(data["results"]) == 3
        assert data["results"][0]["url"] == urls[0]
        assert data["results"][1]["url"] == urls[1]
        assert data["results"][2]["url"] == urls[2]

    @patch('app.api.routes.process_url')
    def test_handles_all_failures(self, mock_process):
        """Test handling when all URLs fail"""
        # Arrange
        mock_process.return_value = {
            "url": "https://example.com/failed",
            "title": None,
            "extraction_success": False,
            "metrics": None,
            "error": "Extraction failed"
        }

        # Act
        response = client.post(
            "/api/analyze-urls",
            json={"urls": [
                "https://example.com/1",
                "https://example.com/2"
            ]}
        )

        # Assert
        data = response.json()
        assert data["summary"]["total_urls"] == 2
        assert data["summary"]["successful"] == 0
        assert data["summary"]["failed"] == 2
        assert data["summary"]["average_grade_level"] is None

    @patch('app.api.routes.process_url')
    def test_large_batch_processing(self, mock_process):
        """Test processing 100+ URLs"""
        # Arrange
        urls = [f"https://example.com/{i}" for i in range(100)]

        mock_process.return_value = {
            "url": "https://example.com/test",
            "title": "Test",
            "extraction_success": True,
            "metrics": {
                "flesch_kincaid_grade": 10.0,
                "smog": 10.0,
                "coleman_liau": 10.0,
                "ari": 10.0,
                "consensus": 10.0,
                "word_count": 500,
                "sentence_count": 25
            },
            "error": None
        }

        # Act
        response = client.post(
            "/api/analyze-urls",
            json={"urls": urls}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 100
        assert data["summary"]["total_urls"] == 100
        assert mock_process.call_count == 100


class TestSummaryCalculations:
    """Test summary statistics calculations"""

    @patch('app.api.routes.process_url')
    def test_average_grade_level_calculation(self, mock_process):
        """Test that average grade level is calculated correctly"""
        # Arrange
        mock_process.side_effect = [
            {"url": "1", "extraction_success": True, "metrics": {
                "flesch_kincaid_grade": 8.0, "smog": 8.0,
                "coleman_liau": 8.0, "ari": 8.0, "consensus": 8.0,
                "word_count": 100, "sentence_count": 5
            }, "title": "1", "error": None},
            {"url": "2", "extraction_success": True, "metrics": {
                "flesch_kincaid_grade": 12.0, "smog": 12.0,
                "coleman_liau": 12.0, "ari": 12.0, "consensus": 12.0,
                "word_count": 100, "sentence_count": 5
            }, "title": "2", "error": None},
            {"url": "3", "extraction_success": True, "metrics": {
                "flesch_kincaid_grade": 10.0, "smog": 10.0,
                "coleman_liau": 10.0, "ari": 10.0, "consensus": 10.0,
                "word_count": 100, "sentence_count": 5
            }, "title": "3", "error": None},
        ]

        # Act
        response = client.post(
            "/api/analyze-urls",
            json={"urls": ["1", "2", "3"]}
        )

        # Assert
        data = response.json()
        # Average of 8.0, 12.0, 10.0 = 10.0
        assert data["summary"]["average_grade_level"] == 10.0

    @patch('app.api.routes.process_url')
    def test_average_excludes_failed_urls(self, mock_process):
        """Test that failed URLs don't affect average"""
        # Arrange
        mock_process.side_effect = [
            {"url": "1", "extraction_success": True, "metrics": {
                "flesch_kincaid_grade": 10.0, "smog": 10.0,
                "coleman_liau": 10.0, "ari": 10.0, "consensus": 10.0,
                "word_count": 100, "sentence_count": 5
            }, "title": "1", "error": None},
            {"url": "2", "extraction_success": False, "metrics": None,
             "title": None, "error": "Failed"},
            {"url": "3", "extraction_success": True, "metrics": {
                "flesch_kincaid_grade": 12.0, "smog": 12.0,
                "coleman_liau": 12.0, "ari": 12.0, "consensus": 12.0,
                "word_count": 100, "sentence_count": 5
            }, "title": "3", "error": None},
        ]

        # Act
        response = client.post(
            "/api/analyze-urls",
            json={"urls": ["1", "2", "3"]}
        )

        # Assert
        data = response.json()
        # Average of only 10.0 and 12.0 = 11.0
        assert data["summary"]["average_grade_level"] == 11.0
        assert data["summary"]["successful"] == 2
        assert data["summary"]["failed"] == 1
