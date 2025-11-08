"""
Comprehensive testing with diverse article types and edge cases
"""
import time
from app.services.extraction import extract_text
from app.services.readability import analyze_text

# Comprehensive test dataset
TEST_DATASET = {
    "NGPF Articles": [
        "https://www.ngpf.org/blog/advocacy/what-is-mission-2030/",
        "https://www.ngpf.org/blog/advocacy/2024-financial-education-advocacy-trends/",
        "https://www.ngpf.org/blog/best-of/best-of-2024-top-questions-of-the-day/",
        "https://www.ngpf.org/blog/fincap-friday/fincap-friday-fed-up/",
        "https://www.ngpf.org/blog/question-of-the-day/question-of-the-day-what-is-one-of-the-top-3-financial-resolutions-for-the-new-year/",
    ],
    "News Articles": [
        "https://apnews.com/article/flight-cuts-government-shutdown-airlines-c21ffa6c3d55e3d2fe7f53702112727b",
    ],
    "Reference": [
        "https://en.wikipedia.org/wiki/Readability",
    ],
    "Edge Cases": [
        "https://example.com",  # Should fail
        "invalid-url",  # Invalid format
        "https://httpstat.us/404",  # 404 error
    ]
}

def run_comprehensive_test():
    """Run comprehensive testing suite"""

    print("\n" + "="*80)
    print("COMPREHENSIVE TEST SUITE")
    print("="*80 + "\n")

    all_results = {}
    total_time = 0
    total_urls = 0

    for category, urls in TEST_DATASET.items():
        print(f"\n{'='*80}")
        print(f"CATEGORY: {category}")
        print(f"{'='*80}\n")

        category_results = []

        for i, url in enumerate(urls, 1):
            total_urls += 1
            print(f"[{i}/{len(urls)}] Testing: {url[:70]}...")

            # Measure performance
            start_time = time.time()
            extraction = extract_text(url)
            extraction_time = time.time() - start_time
            total_time += extraction_time

            if not extraction.success:
                print(f"    [FAILED] {extraction.error}")
                print(f"    Time: {extraction_time:.2f}s\n")
                category_results.append({
                    'url': url,
                    'success': False,
                    'error': extraction.error,
                    'time': extraction_time
                })
                continue

            # Analyze
            metrics = analyze_text(extraction.text)

            if not metrics:
                print(f"    [FAILED] Analysis error")
                print(f"    Time: {extraction_time:.2f}s\n")
                category_results.append({
                    'url': url,
                    'success': False,
                    'error': 'Analysis failed',
                    'time': extraction_time
                })
                continue

            # Success
            print(f"    [SUCCESS]")
            print(f"    Method: {extraction.extraction_method}")
            print(f"    Words: {metrics.word_count:,}")
            print(f"    Reading Level: {metrics.consensus:.1f}")
            print(f"    Time: {extraction_time:.2f}s\n")

            category_results.append({
                'url': url,
                'success': True,
                'method': extraction.extraction_method,
                'words': metrics.word_count,
                'grade_level': metrics.consensus,
                'time': extraction_time
            })

        all_results[category] = category_results

    # Print overall summary
    print("\n" + "="*80)
    print("OVERALL SUMMARY")
    print("="*80 + "\n")

    total_successful = sum(1 for cat in all_results.values() for r in cat if r['success'])
    total_failed = total_urls - total_successful
    success_rate = (total_successful / total_urls * 100) if total_urls > 0 else 0

    print(f"Total URLs Tested: {total_urls}")
    print(f"Successful: {total_successful}")
    print(f"Failed: {total_failed}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Average Time: {total_time/total_urls:.2f}s per URL\n")

    # Category breakdown
    print("Category Breakdown:")
    for category, results in all_results.items():
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        print(f"\n  {category}:")
        print(f"    Success: {successful}/{total}")

        if successful > 0:
            successful_results = [r for r in results if r['success']]
            avg_words = sum(r['words'] for r in successful_results) / successful
            avg_grade = sum(r['grade_level'] for r in successful_results) / successful
            avg_time = sum(r['time'] for r in successful_results) / successful

            print(f"    Avg Words: {avg_words:,.0f}")
            print(f"    Avg Grade Level: {avg_grade:.1f}")
            print(f"    Avg Time: {avg_time:.2f}s")

    # Performance analysis
    print("\n" + "="*80)
    print("PERFORMANCE ANALYSIS")
    print("="*80 + "\n")

    all_times = [r['time'] for cat in all_results.values() for r in cat]
    if all_times:
        print(f"Fastest: {min(all_times):.2f}s")
        print(f"Slowest: {max(all_times):.2f}s")
        print(f"Average: {sum(all_times)/len(all_times):.2f}s")

        under_2s = sum(1 for t in all_times if t < 2.0)
        print(f"Under 2s target: {under_2s}/{len(all_times)} ({under_2s/len(all_times)*100:.1f}%)")

    # Edge case validation
    print("\n" + "="*80)
    print("EDGE CASE VALIDATION")
    print("="*80 + "\n")

    edge_results = all_results.get("Edge Cases", [])
    print("Expected: All edge cases should fail gracefully")
    for result in edge_results:
        status = "[PASS]" if not result['success'] else "[UNEXPECTED SUCCESS]"
        print(f"{status} {result['url'][:50]}")
        if not result['success']:
            print(f"        Error: {result['error']}")

    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80 + "\n")

    # Final verdict
    if success_rate >= 90 and total_time / total_urls < 2.5:
        print("[PASS] All acceptance criteria met!")
        print(f"  - Success rate: {success_rate:.1f}% (target: >90%)")
        print(f"  - Average time: {total_time/total_urls:.2f}s (target: <2.5s)")
    else:
        print("[NEEDS IMPROVEMENT]")
        if success_rate < 90:
            print(f"  - Success rate: {success_rate:.1f}% (target: >90%)")
        if total_time / total_urls >= 2.5:
            print(f"  - Average time: {total_time/total_urls:.2f}s (target: <2.5s)")

    return all_results


if __name__ == "__main__":
    run_comprehensive_test()
