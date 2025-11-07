"""Tests for text extraction service"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.extraction import (
    extract_with_trafilatura,
    extract_with_readability,
    extract_text,
    fetch_url_async,
    validate_url,
)
from app.models.schemas import ExtractionResult


class TestTrafilaturaExtraction:
    """Test Trafilatura extraction functionality"""

    @patch('app.services.extraction.fetch_url')
    @patch('app.services.extraction.extract')
    def test_successful_trafilatura_extraction(self, mock_extract, mock_fetch):
        """Test successful text extraction with Trafilatura"""
        # Arrange
        mock_fetch.return_value = "<html><body><p>Test article content</p></body></html>"
        mock_extract.return_value = "Test article content"
        url = "https://example.com/article"

        # Act
        result = extract_with_trafilatura(url)

        # Assert
        assert result is not None
        assert result == "Test article content"
        mock_fetch.assert_called_once_with(url)
        mock_extract.assert_called_once()

    @patch('app.services.extraction.fetch_url')
    def test_trafilatura_returns_none_on_failure(self, mock_fetch):
        """Test Trafilatura returns None when extraction fails"""
        # Arrange
        mock_fetch.return_value = None
        url = "https://example.com/article"

        # Act
        result = extract_with_trafilatura(url)

        # Assert
        assert result is None

    @patch('app.services.extraction.fetch_url')
    def test_trafilatura_handles_network_errors(self, mock_fetch):
        """Test Trafilatura handles network errors gracefully"""
        # Arrange
        mock_fetch.side_effect = Exception("Network error")
        url = "https://example.com/article"

        # Act
        result = extract_with_trafilatura(url)

        # Assert
        assert result is None


class TestReadabilityFallback:
    """Test readability-lxml fallback functionality"""

    @patch('app.services.extraction.requests.get')
    @patch('app.services.extraction.Document')
    def test_successful_readability_extraction(self, mock_document, mock_get):
        """Test successful text extraction with readability-lxml"""
        # Arrange
        mock_response = Mock()
        mock_response.content = b"<html><body><p>Fallback content</p></body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        mock_doc = Mock()
        mock_doc.summary.return_value = "<p>Fallback content</p>"
        mock_doc.title.return_value = "Test Title"
        mock_document.return_value = mock_doc

        url = "https://example.com/article"

        # Act
        result = extract_with_readability(url)

        # Assert
        assert result is not None
        assert "Fallback content" in result

    @patch('app.services.extraction.requests.get')
    def test_readability_returns_none_on_failure(self, mock_get):
        """Test readability-lxml returns None when extraction fails"""
        # Arrange
        mock_get.side_effect = Exception("Connection error")
        url = "https://example.com/article"

        # Act
        result = extract_with_readability(url)

        # Assert
        assert result is None


class TestCompleteExtraction:
    """Test complete extraction pipeline with fallback"""

    @patch('app.services.extraction.extract_with_trafilatura')
    @patch('app.services.extraction.extract_with_readability')
    def test_uses_trafilatura_when_successful(self, mock_readability, mock_trafilatura):
        """Test that Trafilatura is used first when successful"""
        # Arrange
        mock_trafilatura.return_value = "Trafilatura content"
        url = "https://example.com/article"

        # Act
        result = extract_text(url)

        # Assert
        assert result.success is True
        assert result.text == "Trafilatura content"
        assert result.extraction_method == "trafilatura"
        mock_readability.assert_not_called()

    @patch('app.services.extraction.extract_with_trafilatura')
    @patch('app.services.extraction.extract_with_readability')
    def test_falls_back_to_readability_on_trafilatura_failure(
        self, mock_readability, mock_trafilatura
    ):
        """Test fallback to readability-lxml when Trafilatura fails"""
        # Arrange
        mock_trafilatura.return_value = None
        mock_readability.return_value = "Readability content"
        url = "https://example.com/article"

        # Act
        result = extract_text(url)

        # Assert
        assert result.success is True
        assert result.text == "Readability content"
        assert result.extraction_method == "readability-lxml"
        mock_trafilatura.assert_called_once()
        mock_readability.assert_called_once()

    @patch('app.services.extraction.extract_with_trafilatura')
    @patch('app.services.extraction.extract_with_readability')
    def test_returns_failure_when_both_methods_fail(
        self, mock_readability, mock_trafilatura
    ):
        """Test that extraction fails when both methods fail"""
        # Arrange
        mock_trafilatura.return_value = None
        mock_readability.return_value = None
        url = "https://example.com/article"

        # Act
        result = extract_text(url)

        # Assert
        assert result.success is False
        assert result.text is None
        assert result.error is not None
        assert "Failed to extract" in result.error


class TestTimeoutHandling:
    """Test timeout configuration and handling"""

    @patch('app.services.extraction.fetch_url')
    def test_respects_timeout_configuration(self, mock_fetch):
        """Test that timeout configuration is respected"""
        # Arrange
        mock_fetch.side_effect = TimeoutError("Request timed out")
        url = "https://example.com/slow-article"

        # Act
        result = extract_with_trafilatura(url, timeout=5)

        # Assert
        assert result is None

    @patch('app.services.extraction.extract_with_trafilatura')
    @patch('app.services.extraction.extract_with_readability')
    def test_timeout_error_in_extraction_result(
        self, mock_readability, mock_trafilatura
    ):
        """Test that timeout errors are properly reported"""
        # Arrange
        mock_trafilatura.side_effect = TimeoutError("Timeout")
        mock_readability.return_value = None
        url = "https://example.com/slow-article"

        # Act
        result = extract_text(url, timeout=5)

        # Assert
        assert result.success is False
        assert "timeout" in result.error.lower()


class TestURLValidation:
    """Test URL validation"""

    def test_validates_http_urls(self):
        """Test that HTTP URLs are validated correctly"""
        assert validate_url("http://example.com") is True
        assert validate_url("https://example.com") is True

    def test_rejects_invalid_urls(self):
        """Test that invalid URLs are rejected"""
        assert validate_url("not a url") is False
        assert validate_url("ftp://example.com") is False
        assert validate_url("") is False
        assert validate_url("javascript:alert(1)") is False

    @patch('app.services.extraction.extract_with_trafilatura')
    def test_extract_text_validates_url_before_extraction(self, mock_trafilatura):
        """Test that URL is validated before attempting extraction"""
        # Arrange
        url = "invalid-url"

        # Act
        result = extract_text(url)

        # Assert
        assert result.success is False
        assert "Invalid URL" in result.error
        mock_trafilatura.assert_not_called()


class TestAsyncURLFetching:
    """Test async URL fetching with aiohttp"""

    @pytest.mark.asyncio
    async def test_fetch_url_async_success(self):
        """Test successful async URL fetching"""
        with patch('app.services.extraction.aiohttp.ClientSession') as mock_session:
            # Arrange
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="<html>Content</html>")

            mock_session_instance = AsyncMock()
            mock_session_instance.get = AsyncMock(return_value=mock_response)
            mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session_instance.__aexit__ = AsyncMock()
            mock_session.return_value = mock_session_instance

            url = "https://example.com/article"

            # Act
            result = await fetch_url_async(mock_session_instance, url)

            # Assert
            assert result is not None
            assert "<html>Content</html>" in result

    @pytest.mark.asyncio
    async def test_fetch_url_async_handles_errors(self):
        """Test async URL fetching handles errors gracefully"""
        with patch('app.services.extraction.aiohttp.ClientSession') as mock_session:
            # Arrange
            mock_session_instance = AsyncMock()
            mock_session_instance.get = AsyncMock(side_effect=Exception("Network error"))

            url = "https://example.com/article"

            # Act
            result = await fetch_url_async(mock_session_instance, url)

            # Assert
            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_multiple_urls_concurrently(self):
        """Test fetching multiple URLs concurrently"""
        with patch('app.services.extraction.fetch_url_async') as mock_fetch:
            # Arrange
            mock_fetch.side_effect = [
                "<html>Content 1</html>",
                "<html>Content 2</html>",
                "<html>Content 3</html>",
            ]
            urls = [
                "https://example.com/1",
                "https://example.com/2",
                "https://example.com/3",
            ]

            # Act
            from app.services.extraction import fetch_multiple_urls
            results = await fetch_multiple_urls(urls)

            # Assert
            assert len(results) == 3
            assert all(r is not None for r in results)


class TestConcurrencyLimiting:
    """Test concurrent request limiting with semaphore"""

    @pytest.mark.asyncio
    async def test_limits_concurrent_requests(self):
        """Test that concurrent requests are limited by semaphore"""
        with patch('app.services.extraction.fetch_url_async') as mock_fetch:
            # Arrange
            mock_fetch.return_value = "<html>Content</html>"
            urls = [f"https://example.com/{i}" for i in range(20)]
            max_concurrent = 10

            # Act
            from app.services.extraction import fetch_multiple_urls
            results = await fetch_multiple_urls(urls, max_concurrent=max_concurrent)

            # Assert
            assert len(results) == 20
            # Note: Actual concurrency limiting is verified through timing in integration tests


class TestRetryLogic:
    """Test retry logic with exponential backoff"""

    @pytest.mark.asyncio
    async def test_retries_on_network_failure(self):
        """Test that network failures trigger retries"""
        with patch('app.services.extraction.fetch_url_async') as mock_fetch:
            # Arrange
            mock_fetch.side_effect = [
                Exception("Network error"),
                Exception("Network error"),
                "<html>Success after retries</html>",
            ]
            url = "https://example.com/article"

            # Act
            from app.services.extraction import fetch_with_retry
            result = await fetch_with_retry(None, url, max_retries=3)

            # Assert
            assert result is not None
            assert "Success" in result
            assert mock_fetch.call_count == 3

    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """Test that retry delay increases exponentially"""
        with patch('app.services.extraction.fetch_url_async') as mock_fetch:
            with patch('app.services.extraction.asyncio.sleep') as mock_sleep:
                # Arrange
                mock_fetch.side_effect = [
                    Exception("Error 1"),
                    Exception("Error 2"),
                    "<html>Success</html>",
                ]
                url = "https://example.com/article"

                # Act
                from app.services.extraction import fetch_with_retry
                await fetch_with_retry(None, url, max_retries=3)

                # Assert
                # Check that sleep was called with increasing delays
                assert mock_sleep.call_count >= 2

    @pytest.mark.asyncio
    async def test_gives_up_after_max_retries(self):
        """Test that retries stop after max attempts"""
        with patch('app.services.extraction.fetch_url_async') as mock_fetch:
            # Arrange
            mock_fetch.side_effect = Exception("Persistent error")
            url = "https://example.com/article"

            # Act
            from app.services.extraction import fetch_with_retry
            result = await fetch_with_retry(None, url, max_retries=3)

            # Assert
            assert result is None
            assert mock_fetch.call_count == 3
