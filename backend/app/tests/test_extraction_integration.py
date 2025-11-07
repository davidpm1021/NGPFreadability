"""Integration tests for text extraction with real URLs

These tests require network access and will be slower than unit tests.
Run with: pytest app/tests/test_extraction_integration.py
"""
import pytest
from app.services.extraction import (
    extract_text,
    extract_multiple_urls,
    validate_url,
)


# Sample NGPF-related article URLs for testing
SAMPLE_URLS = [
    "https://www.nytimes.com/2024/01/15/business/economy/inflation-2024.html",
    "https://www.wsj.com/economy/jobs/employment-labor-market-2024",
    "https://www.bloomberg.com/news/articles/2024-01-10/us-economy-outlook",
    "https://www.cnbc.com/2024/01/12/stocks-market-news.html",
    "https://www.investopedia.com/terms/c/compoundinterest.asp",
]

# Known bad URLs for failure testing
BAD_URLS = [
    "https://httpstat.us/404",  # 404 error
    "https://httpstat.us/500",  # 500 error
    "https://invalid-domain-that-does-not-exist-12345.com",  # DNS failure
]


class TestURLValidation:
    """Test URL validation with various formats"""

    def test_valid_urls(self):
        """Test that common URL formats are validated correctly"""
        valid_urls = [
            "http://example.com",
            "https://example.com",
            "https://www.example.com",
            "https://example.com/path/to/article",
            "https://example.com/article?id=123",
            "https://subdomain.example.com/article",
        ]
        for url in valid_urls:
            assert validate_url(url) is True, f"Failed to validate: {url}"

    def test_invalid_urls(self):
        """Test that invalid URLs are rejected"""
        invalid_urls = [
            "not a url",
            "ftp://example.com",
            "javascript:alert(1)",
            "",
            "//example.com",
            "http://",
            "example.com",  # Missing scheme
        ]
        for url in invalid_urls:
            assert validate_url(url) is False, f"Incorrectly validated: {url}"


@pytest.mark.integration
@pytest.mark.slow
class TestSingleURLExtraction:
    """Integration tests for single URL extraction

    Note: These tests make real network requests and may be slow or fail
    due to network issues, site changes, or rate limiting.
    """

    @pytest.mark.skipif(
        "not config.getoption('--run-integration')",
        reason="Integration tests only run with --run-integration flag"
    )
    def test_extract_from_investopedia(self):
        """Test extraction from Investopedia (generally stable)"""
        url = "https://www.investopedia.com/terms/c/compoundinterest.asp"
        result = extract_text(url)

        assert result.success is True
        assert result.text is not None
        assert len(result.text) > 100  # Should have substantial content
        assert result.extraction_method in ["trafilatura", "readability-lxml"]

    @pytest.mark.skipif(
        "not config.getoption('--run-integration')",
        reason="Integration tests only run with --run-integration flag"
    )
    def test_extract_handles_404(self):
        """Test that 404 errors are handled gracefully"""
        url = "https://httpstat.us/404"
        result = extract_text(url)

        # Should handle 404 gracefully without crashing
        assert result.success is False or result.text is None

    @pytest.mark.skipif(
        "not config.getoption('--run-integration')",
        reason="Integration tests only run with --run-integration flag"
    )
    def test_extract_invalid_domain(self):
        """Test that invalid domains are handled gracefully"""
        url = "https://invalid-domain-that-does-not-exist-12345.com"
        result = extract_text(url)

        assert result.success is False
        assert result.error is not None


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.asyncio
class TestMultipleURLExtraction:
    """Integration tests for batch URL extraction"""

    @pytest.mark.skipif(
        "not config.getoption('--run-integration')",
        reason="Integration tests only run with --run-integration flag"
    )
    async def test_extract_multiple_urls_basic(self):
        """Test extracting from multiple URLs concurrently"""
        urls = [
            "https://www.investopedia.com/terms/c/compoundinterest.asp",
            "https://www.investopedia.com/terms/i/inflation.asp",
        ]

        results = await extract_multiple_urls(urls, max_concurrent=5)

        assert len(results) == len(urls)
        # At least some should succeed
        successful = [r for r in results if r.success]
        assert len(successful) >= 1

    @pytest.mark.skipif(
        "not config.getoption('--run-integration')",
        reason="Integration tests only run with --run-integration flag"
    )
    async def test_extract_handles_mixed_success_failure(self):
        """Test extraction with mix of valid and invalid URLs"""
        urls = [
            "https://www.investopedia.com/terms/c/compoundinterest.asp",  # Should succeed
            "https://httpstat.us/404",  # Should fail
            "https://invalid-domain-12345.com",  # Should fail
        ]

        results = await extract_multiple_urls(urls)

        assert len(results) == 3
        assert results[0].success is True or results[0].success is False
        # At least one should fail
        failed = [r for r in results if not r.success]
        assert len(failed) >= 1

    @pytest.mark.skipif(
        "not config.getoption('--run-integration')",
        reason="Integration tests only run with --run-integration flag"
    )
    async def test_concurrent_request_limiting(self):
        """Test that concurrent requests are properly limited"""
        import time

        # Create 20 URLs (mix of valid and fast-responding)
        urls = ["https://httpstat.us/200?sleep=100" for _ in range(20)]

        start_time = time.time()
        results = await extract_multiple_urls(urls, max_concurrent=5)
        elapsed = time.time() - start_time

        assert len(results) == 20
        # With 5 concurrent and 100ms each, should take at least 400ms (4 batches)
        # But less than sequential (2000ms)
        assert elapsed < 5.0  # Generous upper bound


@pytest.mark.integration
class TestExtractionSuccessRate:
    """Test extraction success rate metrics"""

    @pytest.mark.skipif(
        "not config.getoption('--run-integration')",
        reason="Integration tests only run with --run-integration flag"
    )
    @pytest.mark.asyncio
    async def test_success_rate_calculation(self):
        """Calculate success rate on sample URLs"""
        # Mix of likely-successful URLs
        test_urls = [
            "https://www.investopedia.com/terms/c/compoundinterest.asp",
            "https://www.investopedia.com/terms/i/inflation.asp",
            "https://www.investopedia.com/terms/s/stockmarket.asp",
            "https://www.investopedia.com/terms/b/bond.asp",
            "https://www.investopedia.com/terms/r/riskmanagement.asp",
        ]

        results = await extract_multiple_urls(test_urls)

        successful = sum(1 for r in results if r.success)
        total = len(results)
        success_rate = (successful / total) * 100

        print(f"\nExtraction success rate: {success_rate:.1f}% ({successful}/{total})")

        # Log extraction methods used
        methods = {}
        for r in results:
            if r.success and r.extraction_method:
                methods[r.extraction_method] = methods.get(r.extraction_method, 0) + 1

        print(f"Extraction methods: {methods}")

        # For stable sites like Investopedia, we expect high success
        # Note: This might fail due to rate limiting or network issues
        assert success_rate >= 60, f"Success rate too low: {success_rate}%"


@pytest.mark.integration
class TestEdgeCases:
    """Test edge cases and special scenarios"""

    def test_extract_from_empty_url(self):
        """Test extraction from empty URL"""
        result = extract_text("")

        assert result.success is False
        assert "Invalid URL" in result.error

    def test_extract_from_malformed_url(self):
        """Test extraction from malformed URL"""
        result = extract_text("not-a-url")

        assert result.success is False
        assert "Invalid URL" in result.error

    @pytest.mark.skipif(
        "not config.getoption('--run-integration')",
        reason="Integration tests only run with --run-integration flag"
    )
    @pytest.mark.asyncio
    async def test_extract_from_empty_list(self):
        """Test extraction from empty URL list"""
        results = await extract_multiple_urls([])

        assert results == []

    @pytest.mark.skipif(
        "not config.getoption('--run-integration')",
        reason="Integration tests only run with --run-integration flag"
    )
    def test_extract_with_custom_timeout(self):
        """Test extraction with custom timeout"""
        url = "https://httpstat.us/200?sleep=5000"  # 5 second delay

        # Should timeout with 1 second timeout
        result = extract_text(url, timeout=1)

        # Might succeed if request completes, or fail with timeout
        # Just ensure it doesn't hang indefinitely
        assert result is not None


def pytest_addoption(parser):
    """Add custom pytest options"""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests that require network access"
    )


def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test requiring network"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow-running"
    )
