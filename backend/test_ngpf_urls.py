"""
Test extraction with multiple NGPF URLs to validate quality
"""
from app.services.extraction import extract_text
from app.services.readability import analyze_text

# Sample NGPF URLs to test
TEST_URLS = [
    "https://www.ngpf.org/blog/advocacy/what-is-mission-2030/",
    "https://www.ngpf.org/blog/advocacy/2024-financial-education-advocacy-trends/",
    "https://www.ngpf.org/blog/best-of/best-of-2024-top-questions-of-the-day/",
    "https://www.ngpf.org/blog/fincap-friday/fincap-friday-fed-up/",
    "https://www.ngpf.org/blog/question-of-the-day/question-of-the-day-what-is-one-of-the-top-3-financial-resolutions-for-the-new-year/",
]

def test_ngpf_extraction():
    """Test extraction on NGPF URLs and report results"""

    print("\n" + "="*80)
    print("NGPF URL EXTRACTION TEST")
    print("="*80 + "\n")

    results = []

    for i, url in enumerate(TEST_URLS, 1):
        print(f"\n[{i}/{len(TEST_URLS)}] Testing: {url}")
        print("-" * 80)

        # Extract text
        extraction = extract_text(url)

        if not extraction.success:
            print(f"[FAILED]: {extraction.error}")
            results.append({
                'url': url,
                'success': False,
                'error': extraction.error
            })
            continue

        # Analyze readability
        metrics = analyze_text(extraction.text)

        if not metrics:
            print(f"[FAILED]: Could not analyze text")
            results.append({
                'url': url,
                'success': False,
                'error': 'Analysis failed'
            })
            continue

        # Success - print summary
        print(f"[SUCCESS]")
        print(f"   Method: {extraction.extraction_method}")
        print(f"   Title: {extraction.title or 'N/A'}")
        print(f"   Words: {metrics.word_count:,}")
        print(f"   Sentences: {metrics.sentence_count}")
        print(f"   Reading Level: {metrics.consensus:.1f}")

        # Check text quality
        text_preview = extraction.text[:200].replace('\n', ' ')
        print(f"   Preview: {text_preview}...")

        # Store result
        results.append({
            'url': url,
            'success': True,
            'method': extraction.extraction_method,
            'words': metrics.word_count,
            'sentences': metrics.sentence_count,
            'grade_level': metrics.consensus,
            'flesch_kincaid': metrics.flesch_kincaid_grade,
            'smog': metrics.smog,
            'coleman_liau': metrics.coleman_liau,
            'ari': metrics.ari
        })

    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful

    print(f"\nTotal URLs: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

    if successful > 0:
        avg_words = sum(r['words'] for r in results if r['success']) / successful
        avg_grade = sum(r['grade_level'] for r in results if r['success']) / successful

        print(f"\nAverage Word Count: {avg_words:,.0f}")
        print(f"Average Reading Level: {avg_grade:.1f}")

        # Show range
        grade_levels = [r['grade_level'] for r in results if r['success']]
        print(f"Reading Level Range: {min(grade_levels):.1f} - {max(grade_levels):.1f}")

    # Show any failures
    if failed > 0:
        print("\nFailed URLs:")
        for r in results:
            if not r['success']:
                print(f"  - {r['url']}")
                print(f"    Error: {r['error']}")

    print("\n" + "="*80)

    return results


if __name__ == "__main__":
    results = test_ngpf_extraction()
